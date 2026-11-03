struct Base {
    int base;
    Base(int v = 0) : base(v) {}
};

struct Mid : virtual Base {
    int mid;
    Mid() : Base(0), mid(0) {}
};

struct Other {
    int other;
    Other(int v = 0) : other(v) {}
};

struct Leaf : Mid, Other {
    int leaf;
    Leaf() : Base(7), Other(1), leaf(2) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Leaf obj;
    return obj.leaf;
}
