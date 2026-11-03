#include <cstddef>
#include <cstdio>
#include <string>
#include <vector>

std::string joinWords(const std::vector<std::string>& words, char separator) {
    std::string joined;
    std::size_t index = 0;
    std::size_t count = words.size();
    for (index = 0; index < count; ++index) {
        if (index > 0) {
            joined.push_back(separator);
        }
        joined += words[index];
    }
    return joined;
}

int main() {
    std::vector<std::string> words;
    std::string text;
    words.push_back("alpha");
    words.push_back("beta");
    text = joinWords(words, ',');
    std::printf("%s\n", text.c_str());
    return 0;
}
