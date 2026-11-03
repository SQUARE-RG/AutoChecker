#include <cstring>
#include <string>
#include <iostream>

std::string copyText(const char* source) {
    std::string buffer(32, '\0');
    std::strncpy(buffer.data(), source, buffer.size() - 1);
    buffer[buffer.size() - 1] = '\0';
    return buffer;
}

int main() {
    const char* source = "string buffer";
    std::string result = copyText(source);
    std::cout << result << '\n';
    return 0;
}
