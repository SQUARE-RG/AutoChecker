#include <iostream>

class Box {
public:
    template<typename T>
    void print(const T& value) const;

    int get() const;

private:
    int data = 42;
};

template<typename T>
void Box::print(const T& value) const {
    std::cout << value << ':' << data << std::endl;
}

int Box::get() const {
    return data;
}

int main() {
    Box box;
    box.print(7);
    return box.get() == 42 ? 0 : 1;
}
