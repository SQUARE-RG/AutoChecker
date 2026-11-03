#include <cstddef>
#include <cstring>
#include <memory>

std::unique_ptr<char[]> copy_text(const char* source, std::size_t capacity) {
    auto result = std::make_unique<char[]>(capacity);
    if (capacity == 0) {
        return result;
    }
    if (source == nullptr) {
        result[0] = '\0';
        return result;
    }
    std::strncpy(result.get(), source, capacity - 1);
    result[capacity - 1] = '\0';
    return result;
}
