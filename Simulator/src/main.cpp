#include <iostream>
#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <stdio.h>
#include <atomic>
#include <thread>
#include <fstream>

#include "cxxopts.hpp"
#include "NFont/NFont.cpp"
#include "cpu.cpp"

#include "fonts/embedded_font.cpp"

#define WINSIZE 512
#define WINSIZESqr 262144
#define surfaceBytesPerPixel 4

bool init();
void deinit();
void createDebugger();
void destroyDebugger();
void createDebugText();
void EventsFunc();
void TickerFunc();
unsigned char asciiFromKeycode(SDL_Keycode kc);

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
    SDL_RenderCopy(renderer, texture, nullptr, nullptr);
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
  destroyDebugger();

  Events.join();
  Ticker.join();

  /* Frees memory */
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

  window = SDL_CreateWindow("Ghost Simulator", /* Title of the SDL window */
			    SDL_WINDOWPOS_CENTERED, /* Position x of the window */
			    SDL_WINDOWPOS_CENTERED, /* Position y of the window */
			    WINSIZE*scale, /* Width of the window in pixels */
			    WINSIZE*scale, /* Height of the window in pixels */
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

  SDL_SetRenderDrawColor(renderer, 255, 0, 255, 1);

  texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING, WINSIZE, WINSIZE);

  if (texture == NULL) {
    std::cout << "Failed to Initialize Texture" << std::endl;
    std::cout << SDL_GetError() << std::endl;
    return false;
  }

  createDebugger();

  std::cout << "Engine Initialized" << std:: endl;

  Events = std::thread(EventsFunc);
  Ticker = std::thread(TickerFunc);
  return true;
}

void createDebugText() {
  // NFont font(dbgrenderer, "../src/fonts/cherry-13-r.bdf", 13);
  SDL_RWops* rwops = SDL_RWFromMem(cherry_13_r_bdf, sizeof(cherry_13_r_bdf));
  NFont font(dbgrenderer, rwops, 0, 13, NFont::Color{255, 255, 255});

  {
    std::stringstream input_text;
	  unsigned short Registers[7] = {};
    processor->readRegisterState(Registers);
    input_text << "| PC 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[0] << " ";
    input_text << "| R0 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[1] << " ";
    input_text << "R1 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[2] << " ";
    input_text << "R2 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[3] << " ";
    input_text << "R3 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[4] << " | ";
    input_text << "DD 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[5] << " ";
    input_text << "AO 0x" << std::hex << std::setw(4) << std::setfill('0') << Registers[6] << " |";
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
      char c = (char)processor->MEMORY[debuggerPage * 64 * 16 + row * 16 + col];
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
  }
}

void destroyDebugger() {
  SDL_DestroyRenderer(dbgrenderer);
  SDL_DestroyWindow(dbgwindow);
}
void createDebugger() {
    dbgwindow = SDL_CreateWindow("Ghost Debugger", /* Title of the SDL window */
			    0, /* Position x of the window */
			    SDL_WINDOWPOS_CENTERED, /* Position y of the window */
			    1580, /* Width of the window in pixels */
			    26*66 + 20, /* Height of the window in pixels */
			    0); /* Additional flag(s) */
  if (dbgwindow == NULL) {
    std::cerr << "SDL window failed to initialise:" << SDL_GetError() << std::endl;
  }
  SDL_HideWindow(dbgwindow);
  dbgrenderer = SDL_CreateRenderer(dbgwindow, -1, 0);
  if (dbgrenderer == NULL) {
    std::cerr << "SDL renderer failed to initialize:" << SDL_GetError() << std::endl;
  }
  createDebugText();
}

void TickerFunc () {
  while (!processor->closed) {
    if (!processor->broken)
      processor->tick();
  }
}

void EventsFunc() {
  while (!processor->closed) {
    if(SDL_PollEvent(&event)) {
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
          if (event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT && event.key.keysym.sym == SDLK_d) {
            if (debuggingPanelActive) {
              SDL_HideWindow(dbgwindow);
              debuggingPanelActive = false;
            } else {
              SDL_ShowWindow(dbgwindow);
              debuggingPanelActive = true;
            }
          } else if (event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT && event.key.keysym.sym == SDLK_h) {
            processor->broken = !processor->broken;
            std::cout << "Debugger break" << std::endl;
          } else if (event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT && event.key.keysym.sym == SDLK_SPACE) {
              if (processor->broken) {
                std::cout << "Debugger step" << std::endl;
                processor->tick();
              } else {
                std::cout << "Couldn't step - still running" << std::endl;
              }
          } else if (event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT && event.key.keysym.sym == SDLK_UP) {
              if (debuggerPage > 0) {
                debuggerPage--;
              }
          } else if (event.key.keysym.mod & KMOD_CTRL && event.key.keysym.mod & KMOD_SHIFT && event.key.keysym.sym == SDLK_DOWN) {
              if (debuggerPage < 63) {
                debuggerPage++;
              }
          } else if (event.key.keysym.sym == SDLK_KP_0) {
            processor->memLog(0, 0x15); // If numpad 0 key pressed, log first 0x15 of memory
          } else {
            processor->keyStateChange(asciiFromKeycode(event.key.keysym.sym), 1);
          }
          break;
        case SDL_KEYUP:
          if (event.key.repeat!=0)
            break;
          processor->keyStateChange(asciiFromKeycode(event.key.keysym.sym), 0);
          break;
        default:
          break;
      }
    }
  }
}

unsigned char asciiFromKeycode(SDL_Keycode kc) {
  return (unsigned char)kc;
}