#include <iostream>

class IntArray {
public:
    IntArray() : values{1, 2, 3} {}

    int operator[](int index) const {
        return values[index];
    }

private:
    int values[3];
};

int main() {
    IntArray arr;
    int value = arr[0];
    std::cout << value << std::endl;
    return 0;
}
