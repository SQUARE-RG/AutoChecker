template <typename T>
class Base {
public:
    T value{};
};

template <typename T>
class Derived : virtual public Base<T> {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    T get() const { return this->value; }
};

int main() {
    Derived<int> d;
    d.value = 42;
    return d.get();
}
