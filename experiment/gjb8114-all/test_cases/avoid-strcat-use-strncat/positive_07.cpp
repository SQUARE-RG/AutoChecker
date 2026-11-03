#include <cstring>

namespace component {

void append_token(char* token, const char* suffix, std::size_t max_len) {
    std::strncat(token, suffix, max_len);
}

}  // namespace component

int main() {
    char token[16] = "abc";
    component::append_token(token, "def", 5);
    return 0;
}
