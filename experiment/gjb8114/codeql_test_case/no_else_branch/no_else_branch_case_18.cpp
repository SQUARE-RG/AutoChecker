#include <stdio.h>
#include <ctype.h>

int classify_character(char ch) {
    if (isdigit(ch)) {
        return 1;
    } else if (isupper(ch)) {
        return 2;
    } else if (islower(ch)) {
        return 3;
    } else if (isspace(ch)) {
        return 4;
    } else {
        return 5;  // 符合：字符处理中包含else
    }
}

int main(void) {
    printf("%d\n", classify_character('A'));
    return 0;
}