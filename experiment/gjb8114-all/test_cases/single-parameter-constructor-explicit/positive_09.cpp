class Flag {
public:
    explicit Flag(bool value) : value_(value) {}
    bool get() const { return value_; }
private:
    bool value_;
};

int main() {
    Flag f(true);
    return f.get() ? 1 : 0;
}
