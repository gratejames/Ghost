#include "out.g"

int main() {
    asm { BRK }
    int arr[3];
    arr[0] = 1;
    arr[1] = 20;
    if (arr[0] + arr[1] == 21) OUTLN("Array indexing OK");
    return 0;
}