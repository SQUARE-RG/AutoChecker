class Counter {
public:
    Counter() : count(0) {}
    int next() {
        count++;
        return count + 1;
    }
private:
    char count; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
};

int main() {
    Counter c;
    return c.next();
}
