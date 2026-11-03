struct Base {
    int base;
    Base(int v = 0) : base(v) {}
};

struct Mid : virtual Base {
    int mid;
    explicit Mid(int v) : Base(v), mid(v) {}
};

struct Other {
    int other;
    explicit Other(int v) : other(v) {}
};

struct Leaf : Mid, Other {
    int leaf;
    Leaf() : Base(3), Mid(1), Other(2), leaf(4) {}
};

int main() {
    Leaf obj;
    return obj.leaf;
}
