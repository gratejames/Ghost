#include <iostream>
#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <stdio.h>
#include <atomic>
#include <thread>
#include <fstream>
#include <vector>

#include "cxxopts.hpp"
#include "NFont/NFont.cpp"
#include "cpu.cpp"
#include "menuBar/menuBar.cpp"

#include "fonts/embedded_font.cpp"

#define WINSIZE 512
#define WINSIZESqr 262144
#define surfaceBytesPerPixel 4

bool init();
void deinit();
void createDebugText();
void EventsFunc();
void TickerFunc();
unsigned char asciiFromKeycode(SDL_Keycode);
void menuBarDraw();
void doAction(std::string);

std::thread Events;
std::thread Ticker;

SDL_Window *window = NULL;
SDL_Renderer *renderer;
SDL_Texture *texture;
Uint32* pixels = nullptr;

SDL_Event event;
cpu *processor;
int scale = 1;

int pitch = 0;

int debuggerPage = 0;
bool debuggingPanelActive = false;
SDL_Window *dbgwindow = NULL;
SDL_Renderer *dbgrenderer;

bool menuBarShown = true;
const int menuBarHeight = 30;
const SDL_Rect menuBarRect = {0, 0, WINSIZE*scale, menuBarHeight};

SDL_Cursor* standardCursor;
SDL_Cursor* interactCursor;
bool mouseInMenuBar = false;
bool mouseInItem = false;


enum DebuggerMode {
  DM_NORMAL,
  DM_JUMP_STACK,
  DM_JUMP_PC,
  DM_FOLLOW_PC
};

int debuggerMode = DM_NORMAL;

std::vector<menuFolder> menuFolders;

int main (int argc, char **argv) {
  cxxopts::Options options("Ghost Simulator SDL", "Simulator for the fantasy console GHOST");
  options.add_options()
    ("v,verbose", "Verbose output")
    ("d,debugging", "Start with debugging panel open")
    ("r,flush", "Flush each debugged character")
    ("s,scale", "Integer scale of the resolution (Integer between 1 and 4)", cxxopts::value<int>())
    ("f,file", "File name", cxxopts::value<std::string>())
    ("h,help", "Print usage")
    ;
  
  auto result = options.parse(argc, argv);


  if (result.count("help")) {
    std::cout << options.help() << std::endl;
    return 0;
  }
  if (result.count("scale")) {
    scale = result["scale"].as<int>();
    if (!(scale == 1 || scale == 2 || scale == 3 || scale == 4)) {
      std::cout << scale << " is an invalid scale" << std::endl;
      return 1;
    }
  }
  
  std::string fileName;
  if (!result.count("file")) {
    std::cout << "No romfile provided (Use -f)" << std::endl;
    return 1;
  } else {
    fileName = result["file"].as<std::string>();
    if (std::ifstream(fileName.c_str()).good()) {
      std::cout << "Loading file: " << fileName << std::endl;
    } else {
      std::cout << "Failed to load file: " << fileName << std::endl;
      return 1;
    }
  }
  processor = new cpu(fileName);
  processor->verbose = result.count("verbose");
  processor->flushDebugChar = result.count("flush");
  bool success = init();
  if (!success) {
    std::cout << "Failed to init" << std::endl;
    return 1;
  }

  if (result.count("debugging")) {
    SDL_ShowWindow(dbgwindow);
    debuggingPanelActive = true;
  }

  while (!processor->closed) {
    SDL_LockTexture(texture, nullptr, (void**)&pixels, &pitch);

    for (int pos = 0; pos < WINSIZESqr; pos++) {
      pixels[pos] = processor->getColorAt(pos);
    }

    SDL_UnlockTexture(texture);
    SDL_RenderClear(renderer);

    SDL_Rect placement = {
      0,
      menuBarHeight*menuBarShown,
      WINSIZE*scale,
      WINSIZE*scale + menuBarHeight*menuBarShown
    };
    SDL_RenderCopy(renderer, texture, nullptr, &placement);
    menuBarDraw();
    SDL_RenderPresent(renderer);
    
    if (debuggingPanelActive) {
      SDL_RenderClear(dbgrenderer);
      createDebugText();
      SDL_RenderPresent(dbgrenderer);
    }
  }
  deinit();

  return 0;
}

void deinit() {
  SDL_FreeCursor(standardCursor);
  SDL_FreeCursor(interactCursor);

  Events.join();
  Ticker.join();

  /* Frees memory */
  SDL_DestroyRenderer(dbgrenderer);
  SDL_DestroyWindow(dbgwindow);

  SDL_DestroyTexture(texture);
  SDL_DestroyRenderer(renderer);
  SDL_DestroyWindow(window);

  /* Shuts down all SDL subsystems */
  SDL_Quit(); 
}

bool init() {
  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL failed to initialise: %s\n", SDL_GetError());
    return false;
  }

  // Create the main window
  window = SDL_CreateWindow("Ghost Simulator", /* Title of the SDL window */
			    SDL_WINDOWPOS_CENTERED, /* Position x of the window */
			    SDL_WINDOWPOS_CENTERED, /* Position y of the window */
			    WINSIZE*scale, /* Width of the window in pixels */
			    WINSIZE*scale + menuBarHeight*menuBarShown, /* Height of the window in pixels */
			    0); /* Additional flag(s) */

  if (window == NULL) {
    fprintf(stderr, "SDL window failed to initialise: %s\n", SDL_GetError());
    return false;
  }

  renderer = SDL_CreateRenderer(window, -1, 0);
  
  if (renderer == NULL) {
    std::cout << "Failed to Initialize Renderer" << std::endl;
    std::cout << SDL_GetError() << std::endl;
    return false;
  }

  SDL_SetRenderDrawColor(renderer, 50, 50, 50, 1); // Menubar color

  texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING, WINSIZE, WINSIZE);

  if (texture == NULL) {
    std::cout << "Failed to Initialize Texture" << std::endl;
    std::cout << SDL_GetError() << std::endl;
    return false;
  }

  // Create the debugger window
  dbgwindow = SDL_CreateWindow("Ghost Debugger", /* Title of the SDL window */
        0, /* Position x of the window */
        SDL_WINDOWPOS_CENTERED, /* Position y of the window */
        1580, /* Width of the window in pixels */
        26*66 + 20, /* Height of the window in pixels */
        0); /* Additional flag(s) */
  if (dbgwindow == NULL) {
    std::cerr << "SDL window failed to initialise:" << SDL_GetError() << std::endl;
    return false;
  }
  SDL_HideWindow(dbgwindow);
  dbgrenderer = SDL_CreateRenderer(dbgwindow, -1, 0);
  if (dbgrenderer == NULL) {
    std::cerr << "SDL renderer failed to initialize:" << SDL_GetError() << std::endl;
    return false;
  }
  createDebugText();

  // Build the menubar structure
  standardCursor = SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_ARROW);
  interactCursor = SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_HAND);

  menuFolder GUI = menuFolder("File");
  GUI.addItem(menuItem("Toggle Menubar", "Ctrl+Shift+m"));
  GUI.addItem(menuItem("Dump ROM", "Ctrl+Shift+e"));
  GUI.addItem(menuItem("Exit", "Ctrl+Shift+q"));
  menuFolders.push_back(GUI);

  menuFolder DBG = menuFolder("Debugger");
  DBG.addItem(menuItem("Toggle Debugger", "Ctrl+Shift+d"));
  DBG.addItem(menuItem("Step", "Ctrl+Shift+space"));
  DBG.addItem(menuItem("Break", "Ctrl+Shift+h"));
  menuFolders.push_back(DBG);

  menuFolder VIEW = menuFolder("View");
  VIEW.addItem(menuItem("Scroll Up", "Ctrl+Shift+up"));
  VIEW.addItem(menuItem("Scroll Down", "Ctrl+Shift+down"));
  VIEW.addItem(menuItem("Page Up", "Ctrl+Shift+pgup"));
  VIEW.addItem(menuItem("Page Down", "Ctrl+Shift+pgdn"));
  VIEW.addItem(menuItem("Jump to PC", "Ctrl+Shift+j"));
  VIEW.addItem(menuItem("Jump to SP", "Ctrl+Shift+p"));
  VIEW.addItem(menuItem("Follow PC", "Ctrl+Shift+f"));
  menuFolders.push_back(VIEW);

  int x = 14*2;
  for(menuFolder& f : menuFolders) {
    f.setPosition(x, 2);
    x += f.getBoundingRect().w + 14*4;
  }

  std::cout << "Engine Initialized" << std:: endl;

  Events = std::thread(EventsFunc);
  Ticker = std::thread(TickerFunc);
  return true;
}

unsigned short getDebugPageOf(unsigned short addr) {
  return addr / (1024);
}

void menuBarDraw() {
  if (!menuBarShown) {
    return;
  }
  SDL_RenderFillRect(renderer, &menuBarRect);
  SDL_RWops* rwops = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont font(renderer, rwops, 0, 13, NFont::Color{255, 255, 255});
  SDL_RWops* rwops2 = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont font2nd(renderer, rwops2, 0, 13, NFont::Color{200, 200, 200});
  for(menuFolder& f : menuFolders) {
    const char* itemText = f.getText().c_str();
    SDL_Rect bound = f.getBoundingRect();
    SDL_Rect boundChildren = f.getBoundingItems();
    if (f.isOpen()) {
      SDL_RenderFillRect(renderer, &boundChildren);
      for (menuItem& i : *f.getItems()) {
        SDL_Rect bound_i = i.getBoundingRect();
        bound_i.w = boundChildren.w;
        if (mouseInItem && i.isHover()) {
          SDL_SetRenderDrawColor(renderer, 100, 100, 100, 1);
          SDL_RenderFillRect(renderer, &bound_i);
          SDL_SetRenderDrawColor(renderer, 50, 50, 50, 1);
        }
        font.draw(renderer, bound_i.x+4, bound_i.y, NFont::Scale(2.0f), i.getText().c_str());
        std::string kt = i.getKeyText();
        int xpos = bound_i.x + bound_i.w - kt.size() * 14 - 4;
        font2nd.draw(renderer, xpos, bound_i.y, NFont::Scale(2.0f), kt.c_str());
      }
    }
    font.draw(renderer, bound.x+4, bound.y, NFont::Scale(2.0f), itemText);
  }
}

void menuBarMouseMove(SDL_Event event) {
  if (!menuBarShown) {
    return;
  }

  bool newMouseInMenuBar = false;
  mouseInItem = false;
  SDL_Point mousePoint = {event.motion.x, event.motion.y};
  for(menuFolder& f : menuFolders) {
    SDL_Rect boundingRect = f.getBoundingRect();
    if (SDL_PointInRect(&mousePoint, &boundingRect)) {
      newMouseInMenuBar = true;
      break;
    }
    SDL_Rect boundingItems = f.getBoundingItems();
    if (f.isOpen() && SDL_PointInRect(&mousePoint, &boundingItems)) {
      newMouseInMenuBar = true;
      for (menuItem& i : *f.getItems()) {
        SDL_Rect bound = i.getBoundingRect();
        bound.w = boundingItems.w;
        i.setHover(SDL_PointInRect(&mousePoint, &bound));
        mouseInItem = true;
      }
      break;
    }
  }
  
  if (newMouseInMenuBar && !mouseInMenuBar) {
    SDL_SetCursor(interactCursor);
    mouseInMenuBar = true;
  } else if (!newMouseInMenuBar && mouseInMenuBar) {
    SDL_SetCursor(standardCursor);
    mouseInMenuBar = false;
  }
}

void menuBarMouseClick(SDL_Event event) {
  if (!menuBarShown || !mouseInMenuBar) {
    return;
  }

  SDL_Point mousePoint = {event.motion.x, event.motion.y};
  for(menuFolder& f : menuFolders) {
    SDL_Rect boundingRect = f.getBoundingRect();
    SDL_Rect boundingItems = f.getBoundingItems();

    if (f.isOpen() && SDL_PointInRect(&mousePoint, &boundingItems)) {
      for (menuItem& i : *f.getItems()) {
        SDL_Rect bound = i.getBoundingRect();
        bound.w = boundingItems.w;
        if (SDL_PointInRect(&mousePoint, &bound)) {
          doAction(i.getText());
        }
      }
    }
    
    if (SDL_PointInRect(&mousePoint, &boundingRect)) {
      std::cout << f.getText() << std::endl;
      f.toggle();
    } else {
      f.close();
    }
  }
}

void doAction(std::string instructionName) {
  if (instructionName == "Exit") {
    processor->verbose = false;
    std::cout << "Engine Closing" << std::endl;
    processor->closed = true;
  } else if (instructionName == "Dump ROM") {
    processor->ROMdump();
  } else if (instructionName == "Toggle Menubar") {
    menuBarShown = !menuBarShown;
    SDL_SetWindowSize(window, WINSIZE*scale, WINSIZE*scale + menuBarHeight*menuBarShown);
  } else if (instructionName == "Toggle Debugger") {
    if (debuggingPanelActive)
      SDL_HideWindow(dbgwindow);
    else
      SDL_ShowWindow(dbgwindow);
    debuggingPanelActive = !debuggingPanelActive;
  } else if (instructionName == "Break") {
    processor->broken = !processor->broken;
    std::cout << "Debugger break" << std::endl;
  } else if (instructionName == "Step") {
    if (processor->broken) {
      std::cout << "Debugger step" << std::endl;
      processor->tick();
    } else {
      std::cout << "Couldn't step - still running" << std::endl;
    }
  } else if (instructionName == "Scroll Up") {
    if (debuggerPage > 0)
      debuggerPage--;
    debuggerMode = DM_NORMAL;
  } else if (instructionName == "Scroll Down") {
    if (debuggerPage < 63)
      debuggerPage++;
    debuggerMode = DM_NORMAL;
  } else if (instructionName == "Page Down") {
    if (debuggerPage < 63-7)
      debuggerPage += 8;
    else
      debuggerPage = 63;
    debuggerMode = DM_NORMAL;
  } else if (instructionName == "Page Up") {
    if (debuggerPage > 0+7)
      debuggerPage -= 8;
    else
      debuggerPage = 0;
    debuggerMode = DM_NORMAL;
  } else if (instructionName == "Jump to PC") {
    debuggerMode = DM_JUMP_PC;
  } else if (instructionName == "Jump to SP") {
    debuggerMode = DM_JUMP_STACK;
  } else if (instructionName == "Follow PC") {
    if (debuggerMode == DM_FOLLOW_PC) {
      debuggerMode = DM_NORMAL;
    } else {
      debuggerMode = DM_FOLLOW_PC;
    }
  } else {
    std::cout << "Internal error, unknown action " << instructionName << std::endl;
  }
}

void createDebugText() {
  SDL_RWops* rwops = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont font(dbgrenderer, rwops, 0, 13, NFont::Color{255, 255, 255});
  SDL_RWops* rwops2 = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont PCfont(dbgrenderer, rwops2, 0, 13, NFont::Color{224, 164, 44});
  SDL_RWops* rwops3 = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont SPfont(dbgrenderer, rwops3, 0, 13, NFont::Color{66, 201, 158});
  unsigned short Registers[9] = {};
  processor->readRegisterState(Registers);
  if (debuggerMode == DM_NORMAL) {
    ;
  } else if (debuggerMode == DM_JUMP_STACK) {
    debuggerPage = getDebugPageOf(0xf000);
    debuggerMode = DM_NORMAL;
  } else if (debuggerMode == DM_JUMP_PC) {
    debuggerPage = getDebugPageOf(Registers[0]);
    debuggerMode = DM_NORMAL;
  } else if (debuggerMode == DM_FOLLOW_PC) {
    debuggerPage = getDebugPageOf(Registers[0]);
  }
  {
    std::stringstream input_text;
    cpu::Instruction inst;
    processor->readCurrentInstruction(inst);
    input_text << std::hex << std::setfill('0');
    input_text << "| PC 0x" << std::setw(4) << Registers[0] << " ";
    input_text << "(" << std::setw(2) << inst.opcode << ":";
    input_text << "" << std::setfill(' ') << std::setw(5) << inst.name << std::setfill('0') << ") ";
    input_text << "| R0 0x" << std::setw(4) << Registers[1] << " ";
    input_text << "R1 0x" << std::setw(4) << Registers[2] << " ";
    input_text << "R2 0x" << std::setw(4) << Registers[3] << " ";
    input_text << "R3 0x" << std::setw(4) << Registers[4] << " | ";
    input_text << "DD 0x" << std::setw(4) << Registers[5] << " ";
    input_text << "AO 0x" << std::setw(4) << Registers[6] << " | ";
    input_text << "SP 0x" << std::setw(4) << Registers[7] << ": ";
    input_text << "0x" << std::setw(4) << Registers[8] << " |";
    font.draw(dbgrenderer, 10, 10+64*26+13, NFont::Scale(2.0f), input_text.str().c_str());
  }

  for (int row = 0; row < 64; row++) {
    std::stringstream input_text;
    input_text << "| 0x" << std::hex << std::setw(4) << std::setfill('0') << debuggerPage * 64 * 16 + row * 16 << " | ";
    for (int col = 0; col < 16; col++) {
	    input_text << std::hex << std::setw(4) << std::setfill('0') << processor->MEMORY[debuggerPage * 64 * 16 + row * 16 + col] << " ";
    }
    input_text << "| ";
    for (int col = 0; col < 16; col++) {
      unsigned short addr = debuggerPage * 64 * 16 + row * 16 + col;
      char c = (char)processor->MEMORY[addr];
      if (c == 0) {
        input_text << ".";
      } else if (c == '%') {
	      input_text << "%%";
      } else if (isprint(c)) {
	      input_text << c;
      } else {
	      input_text << " ";
      }
    }
    input_text << " |";
    font.draw(dbgrenderer, 10, 10 + row*26, NFont::Scale(2.0f), input_text.str().c_str());
    // If on PC page
    if (debuggerPage == getDebugPageOf(Registers[0])) {
      if (row == (Registers[0]%1024)/16) {
        std::stringstream highlight;
        highlight << std::hex << std::setw(4) << std::setfill('0');
        highlight << processor->MEMORY[Registers[0]];
        int PCcol = Registers[0]%16;
        PCfont.draw(dbgrenderer, 10 + (11+PCcol*5)*14, 10 + row*26, NFont::Scale(2.0f), highlight.str().c_str());
      }
    }
    // If on SP page
    if (debuggerPage == getDebugPageOf(0xf000 + Registers[7])) {
      int addr = 0xf000 + Registers[7];
      if (row == (addr%1024)/16) {
        std::stringstream highlight;
        highlight << std::hex << std::setw(4) << std::setfill('0');
        highlight << processor->MEMORY[addr];
        int SPcol = addr%16;
        SPfont.draw(dbgrenderer, 10 + (11+SPcol*5)*14, 10 + row*26, NFont::Scale(2.0f), highlight.str().c_str());
      }
    }
  }
}

void TickerFunc () {
  while (!processor->closed) {
    if (!processor->broken)
      processor->tick();
  }
}

void EventsFunc() {
  while (!processor->closed) {
    if(!SDL_PollEvent(&event)) {
      continue;
    }
    switch (event.type) {
      case SDL_QUIT:
        processor->verbose = false;
        std::cout << "Engine Closing" << std::endl;
        processor->closed = true;
        break;
      case SDL_WINDOWEVENT:
        if (event.window.event == SDL_WINDOWEVENT_CLOSE) {
          processor->verbose = false;
          std::cout << "Engine Closing" << std::endl;
          processor->closed = true;
        }
        break;
      case SDL_KEYDOWN:
        if (event.key.repeat!=0)
          break;
        // If there's ctrl and shift, then it's a simulator keybind
        if (!(event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT)) {
          processor->keyStateChange(asciiFromKeycode(event.key.keysym.sym), 1);
          break;
        }
        switch (event.key.keysym.sym) {
          case SDLK_d:
            doAction("Toggle Debugger");
            break;
          case SDLK_q:
            doAction("Exit");
            break;
          case SDLK_e:
            doAction("Dump ROM");
            break;
          case SDLK_h:
            doAction("Break");
            break;
          case SDLK_SPACE:
            doAction("Step");
            break;
          case SDLK_UP:
            doAction("Scroll Up");
            break;
          case SDLK_DOWN:
            doAction("Scroll Down");
            break;
          case SDLK_PAGEUP:
            doAction("Page Up");
            break;
          case SDLK_PAGEDOWN:
            doAction("Page Down");
            break;
          case SDLK_j:
            doAction("Jump to PC");
            break;
          case SDLK_p:
            doAction("Jump to SP");
            break;
          case SDLK_f:
            doAction("Follow PC");
            break;
          case SDLK_m:
            doAction("Toggle Menubar");
            break;
        }
        break;
      case SDL_KEYUP:
        if (event.key.repeat!=0)
          break;
        processor->keyStateChange(asciiFromKeycode(event.key.keysym.sym), 0);
        break;
      case SDL_MOUSEMOTION:
        menuBarMouseMove(event);
        break;
      case SDL_MOUSEBUTTONDOWN:
        if (event.button.button == SDL_BUTTON_LEFT)
          menuBarMouseClick(event);
        break;
      default:
        break;
    }
  }
}

unsigned char asciiFromKeycode(SDL_Keycode kc) {
  return (unsigned char)kc;
}