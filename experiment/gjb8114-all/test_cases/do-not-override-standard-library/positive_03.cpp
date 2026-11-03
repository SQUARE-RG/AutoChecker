#include <cstring>
#include <iostream>

static const char* find_substring(const char* haystack, const char* needle)
{
    return std::strstr(haystack, needle);
}

int main()
{
    const char* result = find_substring("hello world", "world");
    if (result != nullptr) {
        std::cout << result << '\n';
    }
    return 0;
}
