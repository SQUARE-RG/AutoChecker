#include <string>

int main() {
    std::string text = "/* not a comment */";
    /* ordinary block comment */
    return text.empty() ? 0 : 1;
}
