class Counter {
public:
    explicit Counter(int v) : value(v) {}
    decltype(auto) get() { return value; }
private:
    int value;
};

int main() {
    Counter c(3);
    int x = c.get();
    x = 7;
    return 0;
}
