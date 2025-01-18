#include <iostream>
#include <vector>
#include <SDL2/SDL.h>

class menuItem {
public:
    menuItem(std::string text, std::string keyText);
    SDL_Rect getBoundingRect();
    void setPosition(int, int);
    std::string getText();
    std::string getKeyText();
    void setHover(bool);
    bool isHover();
private:
    std::string text = "";
    std::string keyText = "";
    SDL_Rect boundingRect;
    bool hover = false;
};

class menuFolder {
public:
    menuFolder(std::string);
    SDL_Rect getBoundingRect();
    SDL_Rect getBoundingItems();
    void setPosition(int, int);
    std::string getText();
    void addItem(menuItem);
    void toggle();
    void close();
    bool isOpen();
    std::vector<menuItem>* getItems();
private:
    std::vector<menuItem> items;
    std::string text = "";
    SDL_Rect boundingRect;
    SDL_Rect boundingItems;
    bool open = false;
};