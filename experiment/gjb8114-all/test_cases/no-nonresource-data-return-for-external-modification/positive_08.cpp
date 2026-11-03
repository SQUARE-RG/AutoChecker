#include <iostream>

class Buffer {
public:
    Buffer() {
        arr[0] = 5;
        arr[1] = 6;
        arr[2] = 7;
    }

    const int (&get_array() const)[3] {
        return arr;
    }

private:
    int arr[3];
};

int main() {
    const Buffer b;
    const int (&ref)[3] = b.get_array();
    std::cout << ref[0] << ref[1] << ref[2] << std::endl;
    return 0;
}
