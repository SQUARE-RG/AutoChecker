#include <cstring>
#include <string>
#include <iostream>

int main() {
    using std::strncpy;
    std::string text = "heap safe destination";
    char* buffer = new char[64];
    strncpy(buffer, text.c_str(), 63);
    buffer[63] = '\0';
    std::cout << buffer << '\n';
    delete[] buffer;
    return 0;
}
