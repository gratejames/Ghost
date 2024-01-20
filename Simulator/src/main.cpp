#include <iostream>
#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <stdio.h>
#include <atomic>
#include <thread>
#include <fstream>

#include "cxxopts.hpp"
#include "cpu.cpp"

#define WINSIZE 512
#define WINSIZESqr 262144
#define surfaceBytesPerPixel 4

bool init();
void deinit();
void EventsFunc();
void TickerFunc();
unsigned char asciiFromKeycode(SDL_Keycode kc);

std::thread Events;
std::thread Ticker;

SDL_Window *window = NULL;
SDL_Surface *surface = NULL;
SDL_Renderer *renderer;
SDL_Texture *texture;
Uint32* pixels = nullptr;

SDL_Event event;
cpu *processor;
int scale = 1;

int pitch = 0;

int main (int argc, char **argv) {
  cxxopts::Options options("Ghost Simulator SDL", "Simulator for the fantasy console GHOST");
  options.add_options()
    ("v,verbose", "Verbose output")
    ("r,flush", "Flush each debugged character")
    ("s,scale", "Integer scale of the resolution (Integr between 1 and 4)", cxxopts::value<int>())
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

  while (!processor->closed) {
    SDL_LockTexture(texture, nullptr, (void**)&pixels, &pitch);

    for (int pos = 0; pos < WINSIZESqr; pos++) {
      pixels[pos] = processor->getColorAt(pos);
    }

    SDL_UnlockTexture(texture);
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, texture, nullptr, nullptr);
    SDL_RenderPresent(renderer);
  }
  deinit();

  return 0;
}

void deinit() {
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

  window = SDL_CreateWindow("SDL Example", /* Title of the SDL window */
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

  std::cout << "Engine Initialized" << std:: endl;

  Events = std::thread(EventsFunc);
  Ticker = std::thread(TickerFunc);
  return true;
}

void TickerFunc () {
  while (!processor->closed) {
    processor->tick();
  }
}

void EventsFunc() {
  while (!processor->closed) {
    if(SDL_PollEvent(&event)) {
      switch (event.type) {
        case SDL_QUIT:
          std::cout << "Engine Closing" << std::endl;
          processor->closed = true;
          break;
        case SDL_KEYDOWN:
          if (event.key.repeat!=0)
            break;
          if (event.key.keysym.sym == SDLK_KP_0) {
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