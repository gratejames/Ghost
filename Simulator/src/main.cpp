#include <iostream>
#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include <stdio.h>
#include <atomic>
#include <thread>

#include "cxxopts.hpp"
#include "cpu.cpp"

#define WINSIZE 512
#define WINSIZESqr 262144
#define surfaceBytesPerPixel 4

bool init();
void deinit();
void DrawerFunc();
void TickerFunc();

std::thread Drawer;
std::thread Ticker;

SDL_Window *window = NULL;
SDL_Surface *surface = NULL;
SDL_Event event;
// SDL_PixelFormat* surfacePixelFormat;
// SDL_Color color = {255,255,0};
cpu *processor;

int main (int argc, char **argv)
{
  cxxopts::Options options("Ghost Simulator SDL", "Simulator for the fantasy console GHOST");
  options.add_options()
    ("v,verbose", "Verbose output")
    ("f,file", "File name", cxxopts::value<std::string>())
    ("h,help", "Print usage")
    ;
  
  auto result = options.parse(argc, argv);


  if (result.count("help")) {
    std::cout << options.help() << std::endl;
    return 0;
  }
  
  std::string fileName;
  bool verbose = result.count("verbose");
  if (!result.count("file")) {
    std::cout << "No romfile provided" << std::endl;
    return 1;
  } else {
    fileName = result["file"].as<std::string>();
    std::cout << "Loading file: " << fileName << std::endl;
  }
  processor = new cpu(fileName);
  processor->verbose = verbose;
  bool success = init();
  if (!success) {
    return 1;
  }

  while (1) {
    if (SDL_PollEvent(&event) && event.type == SDL_QUIT) {
      processor->closed = true;
      std::cout << "Engine Closing" << std::endl;
      break;
    }
  }
  deinit();
  
  return 0;
}

void deinit() {
  Drawer.join();
  Ticker.join();
  // processor->debug();
  // std::cout << processor->MEMORY[128*128-1] << std::endl;
  
  /* Frees memory */
  SDL_DestroyWindow(window);

  /* Shuts down all SDL subsystems */
  SDL_Quit(); 
}

bool init() {
  /*
  * Initialises the SDL video subsystem (as well as the events subsystem).
  * Returns 0 on success or a negative error code on failure using SDL_GetError().
  */
  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL failed to initialise: %s\n", SDL_GetError());
    return false;
  }

  /* Creates a SDL window */
  window = SDL_CreateWindow("SDL Example", /* Title of the SDL window */
			    SDL_WINDOWPOS_UNDEFINED, /* Position x of the window */
			    SDL_WINDOWPOS_UNDEFINED, /* Position y of the window */
			    WINSIZE, /* Width of the window in pixels */
			    WINSIZE, /* Height of the window in pixels */
			    0); /* Additional flag(s) */


  /* Checks if window has been created; if not, exits program */
  if (window == NULL) {
    fprintf(stderr, "SDL window failed to initialise: %s\n", SDL_GetError());
    return false;
  }

  surface = SDL_GetWindowSurface(window);

  // surfacePixelFormat = surface->format;
  // int c = SDL_MapRGB(surfacePixelFormat, color.r, color.g, color.b);
  // SDL_FillRect(surface, NULL, c);
  // color = {0, 0, 255};
  SDL_UpdateWindowSurface(window);

  printf("Engine Initialized\n");

  // Drawer = std::thread(DrawerFunc, std::ref(DrawerX));
  Drawer = std::thread(DrawerFunc);
  Ticker = std::thread(TickerFunc);
  return true;
}

void TickerFunc () {
  while (!processor->closed) {
    processor->tick();
  }
}

void DrawerFunc() {
  while (!processor->closed) {
    for (int pos = 0; pos < WINSIZESqr; pos++) {
      Uint32 * const target_pixel = (Uint32 *) ((Uint8 *) surface->pixels + pos*surfaceBytesPerPixel);
      *target_pixel = processor->getColorAt(pos);
    }
    SDL_UpdateWindowSurface(window);
  }
}
