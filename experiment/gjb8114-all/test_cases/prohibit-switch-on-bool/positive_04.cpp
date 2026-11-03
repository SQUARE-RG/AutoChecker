#include <iostream>

int main()
{
    char command = 'x';
    int result = 0;
    switch (command) {
        case 'a':
            result = 1;
            break;
        case 'b':
            result = 2;
            break;
        default:
            result = 3;
            break;
    }
    return result;
}
