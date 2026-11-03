class Counter {
public:
    explicit Counter(int initial = 0) : value_(initial) {}

    const int* raw() const {
        return &value_;
    }

private:
    int value_;
};

int main() {
    Counter counter{1};
    const int* exposed = counter.raw();
    // *exposed = 7; // not allowed
    return 0;
}
