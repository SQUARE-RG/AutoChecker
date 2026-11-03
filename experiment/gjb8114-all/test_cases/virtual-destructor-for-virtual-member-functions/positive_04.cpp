class PlainBase {
public:
    PlainBase() {}
    ~PlainBase() {}
};

class Gadget : public PlainBase {
public:
    Gadget();
    virtual ~Gadget();
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
