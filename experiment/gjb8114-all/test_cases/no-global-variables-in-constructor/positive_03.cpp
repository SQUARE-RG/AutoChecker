int gDefault = 42;

class Device {
public:
    explicit Device(int v);
    int value() const;
private:
    int value_;
};

Device::Device(int v) {
    if (v < 0) {
        value_ = 0;
    } else {
        value_ = v;
    }
}

int Device::value() const {
    return value_;
}

int main() {
    Device d(gDefault);
    return d.value() == 42 ? 0 : 1;
}
