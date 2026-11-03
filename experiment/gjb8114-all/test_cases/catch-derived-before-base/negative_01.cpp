#include <iostream>
class Document {
public:
    Document() : docid(0) {}
    int get_docid() const { return docid; }
private:
    int docid;
};
class Book : public Document {
public:
    Book() : Document(), bookid(0) {}
    int get_bookid() const { return bookid; }
private:
    int bookid;
};
int main() {
    Book mybook;
    try {
        throw mybook;
    }
    catch (Document& d) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << d.get_docid() << std::endl;
    }
    catch (Book& b) {
        std::cout << b.get_bookid() << std::endl;
    }
    return 0;
}
