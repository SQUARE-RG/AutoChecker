#include <string_view>

int main() {
    std::string_view text = "cautious";
    std::string_view part = text.substr(1, 3);
    return static_cast<int>(part.size());
}
