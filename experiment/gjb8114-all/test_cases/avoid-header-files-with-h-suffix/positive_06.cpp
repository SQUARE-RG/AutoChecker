#include <cctype>

int main() {
    int result = std::isalpha('A');
    return result > 0 ? 0 : 1;
}
