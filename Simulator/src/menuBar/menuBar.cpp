#include "menuBar.hpp"

menuFolder::menuFolder(std::string text) {
    this->text = text;
    this->boundingRect.w = 14 * text.length() + 8;
    this->boundingRect.h = 26;
    this->boundingItems.w = 14 * 30;
    this->boundingItems.h = 0;
    this->boundingItems.y = this->boundingRect.h;
}
std::string menuFolder::getText() {
    return this->text;
}
SDL_Rect menuFolder::getBoundingRect() {
    return this->boundingRect;
}
SDL_Rect menuFolder::getBoundingItems() {
    return this->boundingItems;
}

void menuFolder::setPosition(int x, int y) {
    this->boundingRect.x = x;
    this->boundingRect.y = y;
    this->boundingItems.x = x;
    this->boundingItems.y = y + this->boundingRect.h;
    int yi = this->boundingItems.y;
    for (menuItem& item : this->items) {
        item.setPosition(x, yi);
        yi += item.getBoundingRect().h;
    }
}

void menuFolder::addItem(menuItem newItem) {
    this->items.push_back(newItem);
    this->boundingItems.w = std::max(this->boundingItems.w, newItem.getBoundingRect().w);
    newItem.setPosition(this->boundingItems.x, this->boundingItems.y+this->boundingItems.h);
    this->boundingItems.h += newItem.getBoundingRect().h;
}

void menuFolder::toggle() {
    this->open = !this->open;
}

void menuFolder::close() {
    this->open = false;
}

bool menuFolder::isOpen() {
    return this->open;
}

std::vector<menuItem>* menuFolder::getItems() {
    return &(this->items);
}

menuItem::menuItem(std::string text, std::string keyText) {
    this->text = text;
    this->keyText = keyText;
    this->boundingRect.w = 8 + 14 * (text.length() + 5 + keyText.length());
    this->boundingRect.h = 30;
}

SDL_Rect menuItem::getBoundingRect() {
    return this->boundingRect;
}

void menuItem::setPosition(int x, int y) {
    this->boundingRect.x = x;
    this->boundingRect.y = y;
}

std::string menuItem::getText() {
    return this->text;
}

std::string menuItem::getKeyText() {
    return this->keyText;
}

void menuItem::setHover(bool hover) {
    this->hover = hover;
}

bool menuItem::isHover() {
    return this->hover;
}