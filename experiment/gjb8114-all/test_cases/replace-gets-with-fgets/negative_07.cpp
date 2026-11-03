#include <stdio.h>

static void show_input(const char *text)
{
    if (text != nullptr)
    {
        printf("Input: %s\n", text);
    }
}

extern "C" char *gets(char *s)
{
    if (s == nullptr)
    {
        return nullptr;
    }

    char *p = s;
    int ch;
    while ((ch = getchar()) != EOF && ch != '\n')
    {
        *p++ = static_cast<char>(ch);
    }

    if (ch == EOF && p == s)
    {
        return nullptr;
    }

    *p = '\0';
    return s;
}

int main(void)
{
    char line[16] = {0};
    show_input(gets(line)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    return 0;
}
