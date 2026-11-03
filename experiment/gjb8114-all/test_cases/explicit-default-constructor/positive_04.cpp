class Sensor {
public:
    Sensor() noexcept = default;
    explicit Sensor(int id) : id_(id) {}
    int id() const { return id_; }
private:
    int id_ = 0;
};

int main() {
    Sensor s;
    return s.id();
}
