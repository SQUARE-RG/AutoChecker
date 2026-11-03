#include <iostream>

class Holder {
public:
    Holder() : data(new int) {}

    ~Holder() {
        delete data;
        data = nullptr;
    }

    void set(int value) {
        *data = value;
    }

    int get() const {
        return *data;
    }

private:
    int* data;
};

int main() {
    Holder holder;
    holder.set(42);
    std::cout << holder.get() << std::endl;
    return 0;
}
