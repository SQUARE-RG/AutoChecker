#include <cstring>
#include <string>
#include <vector>

void copyIntoVector(std::vector<char>& out, const std::string& in) {
    if (out.empty()) {
        return;
    }
    std::strncpy(out.data(), in.c_str(), out.size() - 1);
    out[out.size() - 1] = '\0';
}

int main() {
    std::vector<char> buffer(8);
    copyIntoVector(buffer, std::string("hello"));
    return 0;
}
