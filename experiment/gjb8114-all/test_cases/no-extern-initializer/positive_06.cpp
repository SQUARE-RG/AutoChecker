#include <string>

extern std::string message;

std::string message("hello");

int main(void)
{
    message += " world";
    return message.empty() ? 1 : 0;
}
