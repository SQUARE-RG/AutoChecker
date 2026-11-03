class Box {
public:
    Box& operator=(const Box& other) {
        value = other.value;
        return *this;
    }

    int value = 0;
};

int main() {
    Box a;
    Box b;
    b.value = 7;
    a = b;
    return a.value;
}
