class Pair {
public:
    explicit Pair(int v);
    int sum() const { return first + second; }
private:
    int first;
    int second;
};

Pair::Pair(int v) : first(v) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
}

int main() {
    Pair p(4);
    return p.sum();
}
