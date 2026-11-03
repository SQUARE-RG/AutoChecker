class MixedInit {
public:
    MixedInit();
    int total() const { return x + y + z; }
private:
    int x;
    int y;
    int z;
};

MixedInit::MixedInit() : x(1), y(2) {
    z = 3;
}

int main() {
    MixedInit m;
    return m.total();
}
