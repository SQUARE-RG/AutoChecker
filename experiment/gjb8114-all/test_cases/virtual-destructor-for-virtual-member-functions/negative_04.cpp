class PlainBase {
public:
    PlainBase() {}
    ~PlainBase() {}
};

class Gadget : public PlainBase {
public:
    Gadget();
    ~Gadget(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual void run();
};

Gadget::Gadget() {}
Gadget::~Gadget() {}
void Gadget::run() {}

int main() {
    Gadget g;
    g.run();
    return 0;
}
