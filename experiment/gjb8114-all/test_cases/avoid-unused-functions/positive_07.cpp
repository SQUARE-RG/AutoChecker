namespace {

template <typename T>
class Box {
public:
    explicit Box(T value) : value_(value) {}

    T value() const {
        return value_;
    }

    void increment() {
        value_ += T{1};
    }

private:
    T value_;
};

} // namespace

int main() {
    Box<int> b(3);
    b.increment();
    return b.value();
}
