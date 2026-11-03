template <typename T> class Box {
public:
    Box() : value(T()) {}
    T get() const { return value; }
    void set(T v) { value = v; }
private:
    T value;
};

int main() {
    Box<int> b;
    b.set(7);
    return b.get();
}
