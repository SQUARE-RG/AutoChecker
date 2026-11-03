class DefaultArgInit {
private:
    int a;
    int b;
public:
    DefaultArgInit(int v = 0) : a(v), b(v) {}
};

int main() {
    DefaultArgInit d;
    DefaultArgInit e(5);
    (void)d;
    (void)e;
    return 0;
}
