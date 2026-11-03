struct A {
    int a;
    explicit A(int v) : a(v) {}
};

struct B {
    int b;
    explicit B(int v) : b(v) {}
};

struct Both : A, B {
    int value;
    Both() : A(1), B(2), value(3) {}
};

int main() {
    Both obj;
    return obj.value;
}
