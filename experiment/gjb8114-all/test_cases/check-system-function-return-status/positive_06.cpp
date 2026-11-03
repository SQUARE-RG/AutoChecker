#include <cstdio>
#include <iostream>

int main() {
    const int result = std::remove("temp_test_file.txt");
    if (result != 0) {
        std::cerr << "failed to remove file, status=" << result << '\n';
        return 1;
    }
    return 0;
}
