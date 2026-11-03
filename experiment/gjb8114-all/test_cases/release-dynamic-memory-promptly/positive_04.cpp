// Positive: constructor allocation is released by the destructor.

class Holder {
public:
    Holder() : data(new int(7)) {}
    ~Holder() { delete data; }

    Holder(const Holder&) = delete;
    Holder& operator=(const Holder&) = delete;

    int get() const { return *data; }

private:
    int* data;
};

int main() {
    Holder holder;
    return holder.get();
}
