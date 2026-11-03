#include <iostream>

enum Chunk {
    kChunkSize = 4
};

int main() {
    int total = 100;
    int quotient = total / static_cast<int>(kChunkSize);
    std::cout << quotient << '\n';
    return 0;
}
