#include <cstdio>
#include <memory>

int summarizeFile() {
    std::shared_ptr<std::FILE> fp(
        std::fopen("numbers.txt", "r"),
        [](std::FILE* file) {
            if (file != nullptr) {
                std::fclose(file);
            }
        });

    if (!fp) {
        return -1;
    }

    int value = 0;
    while (std::fscanf(fp.get(), "%d", &value) == 1) {
        if (value < 0) {
            break;
        }
    }

    return std::ferror(fp.get()) ? -2 : 0;
}

int main() {
    return summarizeFile();
}
