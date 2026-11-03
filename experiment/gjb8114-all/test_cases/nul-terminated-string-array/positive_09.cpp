#include <cstdio>
#include <string>

int main()
{
    std::string text = "yes";
    char buf[8];
    text.copy(buf, text.size());
    buf[text.size()] = '\0';
    std::printf("%s\n", buf);
    return 0;
}
