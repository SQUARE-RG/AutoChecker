template <typename T>
class Base {
public:
    T value{};
};

template <typename T>
class Derived : public Base<T> {
public:
    T get() const { return this->value; }
};

int main() {
    Derived<int> d;
    d.value = 42;
    return d.get();
}
