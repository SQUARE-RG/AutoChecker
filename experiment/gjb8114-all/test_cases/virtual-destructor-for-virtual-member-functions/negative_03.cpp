class Counter {
public:
    Counter() = default;
    ~Counter() {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual void update(int delta) { value += delta; }
    int get() const { return value; }
private:
    int value = 0;
};

int main() {
    Counter c;
    c.update(4);
    return c.get();
}
