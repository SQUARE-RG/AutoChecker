#include <stdio.h>

static void show_input(const char *text)
{
    if (text != nullptr)
    {
        printf("Input: %s\n", text);
    }
}

int main(void)
{
    char line[16] = {0};
    show_input(fgets(line, sizeof line, stdin));
    return 0;
}
