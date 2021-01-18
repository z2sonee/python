import pymysql
from prettytable import PrettyTable

# conn = pymysql.connect(host='127.0.0.1', user='root', password='', port=13306, db='phone_db', charset='utf8')
conn = pymysql.connect(host='172.17.0.2', user='root', password='', port=3306, db='phone_db', charset='utf8')
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 로그인 정보 저장을 위한 싱글톤 
def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class UserLogin:
    def __init__(self):
        pass

    def setUserData(self, mem_id, mem_email, mem_pwd):
        self.mem_id = mem_id
        self.mem_email = mem_email
        self.mem_pwd = mem_pwd

# 장바구니 클래스
class ShopBasket:
    # 상품을 장바구니에 추가 (장바구니 추가시, 상품 정보의 개수는 변하지 않음)
    def add_shopbasket(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        idNum = input("* 장바구니에 담을 핸드폰 정보의 ID를 입력해주세요. -> ")
        while True:
            qtyNum = input("* 원하는 수량을 입력해주세요. -> ")
            if int(qtyNum) >= 1:
                break
            else:
                print("* 1개 이상의 수량을 입력해주세요.")

        # 상품 목록 검색 
        selectSql = 'SELECT * FROM product WHERE prod_id = %s'
        cursor.execute(selectSql, idNum)
        data = cursor.fetchall()

        if len(data) > 0:
            for row in data:
                phone_price = int(row['prod_price'])
                phone_name = row['prod_name']
                phone_qty = int(row['prod_qty'])
            # 수량 충분 -> 장바구니 추가 가능 
            if phone_qty >= int(qtyNum):
                # 장바구니에 추가 
                insertSql = """INSERT INTO shopbasket(mem_id, prod_id, sb_created_date, sb_qty, sb_price) VALUES(%s, %s, NOW(), %s, %s)"""
                cursor.execute(insertSql, (login_info.mem_id, int(idNum), qtyNum, (int(qtyNum) * phone_price)))
                conn.commit()

                print("* 장바구니에 추가가 완료되었습니다! 장바구니 내역을 확인해주세요.")
            # 수량 부족 -> 장바구니 추가 불가능
            else:
                if phone_qty > 0:
                    print("* 수량이 부족하여 장바구니에 추가가 불가능한 상태입니다.")
                    choice = input("* 현재 최대 {0}개까지 추가가 가능합니다. 최대 수량으로 추가하시겠습니까? (예: y, 아니요: n) : ".format(phone_qty))
                    if choice == 'y':
                        # 장바구니에 추가 
                        insertSqls = """INSERT INTO shopbasket(mem_id, prod_id, sb_created_date, sb_qty, sb_price) VALUES(%s, %s, NOW(), %s, %s)"""
                        cursor.execute(insertSqls, (login_info.mem_id, int(idNum), phone_qty, (phone_qty * phone_price)))
                        conn.commit()

                        print("* 장바구니에 추가가 완료되었습니다! 장바구니 내역을 확인해주세요.")
                    else:
                        if choice == 'n':
                            print("* 장바구니 추가가 취소되었습니다.")
                        else:
                            print("* y 또는 n을 입력해주세요.")
                else:
                    print("* 수량이 부족하여 장바구니 추가가 불가능한 상태입니다.")
        else:
            print("* 핸드폰 목록이 없어 장바구니 추가가 불가능합니다.")
            
    # 장바구니 내역 조회
    def show_shopbasket(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        od_selectSql = 'SELECT * FROM shopbasket s, product p, member m WHERE s.prod_id = p.prod_id and s.mem_id = m.mem_id and m.mem_id = %s'
        cursor.execute(od_selectSql, login_info.mem_id)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["장바구니 ID", "고객 이름", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "장바구니 수량", "장바구니 가격($)", "장바구니 추가 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['sb_id'], row['mem_name'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['sb_qty'], row['sb_price'], row['sb_created_date']])
            print("*** 장바구니 내역 조회 ***")
            print(table)
        else:
            print("* 검색 결과가 없습니다.")

    # 장바구니 내역 삭제 
    def delete_shopbasket(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        # 장바구니 내역 출력 
        selectSql = 'SELECT * FROM shopbasket s, product p WHERE s.prod_id = p.prod_id and mem_id = %s'
        cursor.execute(selectSql, (login_info.mem_id))
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["장바구니 ID", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "장바구니 수량", "장바구니 가격($)", "장바구니 추가 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['sb_id'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['sb_qty'], row['sb_price'], row['sb_created_date']])
            print("*** 장바구니 내역 조회 ***")
            print(table)

            idNum = input("* 취소할 장바구니 내역의 ID를 입력해주세요. -> ")

            selSql = 'SELECT * FROM shopbasket WHERE sb_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()

            if len(data) > 0:
                deleteSql = 'DELETE FROM shopbasket WHERE sb_id = %s'
                cursor.execute(deleteSql, int(idNum))
                conn.commit()
                print("* 장바구니에서 삭제되었습니다.")
            else:
                print("* 취소할 장바구니 내역이 존재하지 않습니다.")
        else:
            print("* 취소할 장바구니 내역이 존재하지 않습니다.")

# 관리자 클래스
class Admin:
    # 관리자 로그인 
    def admin_sign_in(self):        
        u_email = input("* 이메일(아이디) : ")
        u_pwd = input("* 비밀번호 : ")

        selectSql = 'SELECT mem_id, mem_name, mem_email, mem_pwd FROM member WHERE mem_email = %s and mem_pwd = %s and mem_email = %s and mem_pwd = %s'
        cursor.execute(selectSql, ('admin', 'admin1234', u_email, u_pwd))
        data = cursor.fetchall()

        if len(data) == 0:
            return 0
        else:
            login_info = UserLogin()
            for row in data:
                print("---------------------------------------------------------------")
                print("* 로그인 성공! 관리자(Admin)님 안녕하세요!".format(row['mem_name']))
                login_info.setUserData(row['mem_id'], row['mem_email'], row['mem_pwd'])
            return 1

    # 전체 주문 내역 조회
    def show_order_list(self):
        allSql = 'SELECT * FROM order_mng o, member m, product p WHERE o.prod_id = p.prod_id and o.mem_id = m.mem_id'
        cursor.execute(allSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["주문 ID", "고객 ID", "고객 이름", "상품명", "색상", "용량(GB)", "주문 수량", "주문 가격($)", "주문 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['order_id'], row['mem_id'], row['mem_name'], row['prod_name'], row['prod_color'], row['prod_volume'], row['order_qty'], row['order_price'], row['order_created_date']])
            print("*** 전체 주문 내역 조회 ***")
            print(table)
        else:
            print("* 주문 검색 결과가 없습니다.")

    # 고객별 주문 내역 조회
    def show_order_bymember(self):
        m_name = input("* 어떤 고객을 기준으로 조회하시겠습니까? (고객 이름 입력) : ")
        m_id =  input("* 입력하신 고객의 ID를 입력해주세요. (고객 ID 입력) : ")

        selectSql = 'SELECT * FROM order_mng o, member m, product p WHERE o.prod_id = p.prod_id and o.mem_id = m.mem_id and m.mem_id = %s and m.mem_name = %s'
        cursor.execute(selectSql, (m_id, m_name))
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["주문 ID", "고객 ID", "고객 이름", "상품명", "색상", "용량(GB)", "주문 수량", "주문 가격($)", "주문 날짜"]
        
        if len(data) > 0:
            total_price = 0
            for row in data:
                table.add_row([row['order_id'], row['mem_id'], row['mem_name'], row['prod_name'], row['prod_color'], row['prod_volume'], row['order_qty'], row['order_price'], row['order_created_date']])
                total_price += int(row['order_price'])
            print("*** 고객별 주문 내역 조회 ***")
            print(table)
            print("* ---> 위 고객의 총 주문 금액은 {0}$ 입니다.".format(total_price))
        else:
            print("* 주문 검색 결과가 없습니다.")

    # 월별/주별 가장 많은 금액을 주문한 고객 정보 조회
    def show_max_price_member(self):
        month = input("* 어떤 월을 기준으로 조회하시겠습니까? (ex: 1) : ")
        week = input("* 어떤 주를 기준으로 조회하시겠습니까? (ex: 2) : ")
        
        # 월별 
        selectSql = 'SELECT m.mem_id, m.mem_name, sum(o.order_price) FROM order_mng o, member m WHERE o.mem_id = m.mem_id and MONTH(o.order_created_date) = %s GROUP BY m.mem_id'
        cursor.execute(selectSql, month)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["고객 ID", "이름", "주문 금액($)"]

        price_list = list()

        if len(data) > 0:
            for row in data:
                table.add_row([row['mem_id'], row['mem_name'], row['sum(o.order_price)']])
                price_list.append(row['sum(o.order_price)'])
            print("*** {0}월의 고객별 총 주문 금액 조회 ***".format(month))
            print(table)
            max_price = max(price_list)

            selSql = 'SELECT m.mem_id, m.mem_name, m.mem_email, m.mem_address, m.mem_phonenum, sum(o.order_price) FROM order_mng o, member m WHERE o.mem_id = m.mem_id and MONTH(o.order_created_date) = %s GROUP BY m.mem_id HAVING sum(o.order_price) = %s'

            cursor.execute(selSql, (month, max_price))
            data2 = cursor.fetchall()

            if len(data2) > 0:
                print("**** 결과 : 월별 가장 많은 금액을 주문한 고객 정보 *****")
                for row in data2:
                    print("* ----> 고객 ID: {0}/ 이름: {1}/ 이메일(아이디): {2}/ 주소: {3}/ 전화번호: {4}/ 총 주문 금액($): {5}".format(row['mem_id'], row['mem_name'], row['mem_email'], row['mem_address'], row['mem_phonenum'], row['sum(o.order_price)']))
            else:
                print("* {0}월에 해당하는 검색 결과가 없습니다.".format(month))
        else:
            print("* {0}월에 해당하는 검색 결과가 없습니다.".format(month))
        
        print("-" * 110)

        # 주별 
        calc_week = 4 * (int(month) - 1) + int(week)
    
        alldateSql = 'SELECT m.mem_id, m.mem_name, sum(o.order_price) FROM order_mng o, member m WHERE o.mem_id = m.mem_id and week(o.order_created_date) = %s GROUP BY m.mem_id'
        cursor.execute(alldateSql, calc_week)
        alldate = cursor.fetchall()

        table2 = PrettyTable()
        table2.field_names = ["고객 ID", "이름", "주문 금액($)"]

        week_price_list = list()

        if len(alldate) > 0:
            for row in alldate:
                table2.add_row([row['mem_id'], row['mem_name'], row['sum(o.order_price)']])
                week_price_list.append(row['sum(o.order_price)'])
            print("*** {0}월 {1}주의 고객별 총 주문 금액 조회 ***".format(month, week))
            print(table2)
            max_price2 = max(week_price_list)

            calcSql = 'SELECT m.mem_id, m.mem_name, m.mem_email, m.mem_address, m.mem_phonenum, sum(o.order_price) FROM order_mng o, member m WHERE o.mem_id = m.mem_id and week(o.order_created_date) = %s GROUP BY m.mem_id HAVING sum(o.order_price) = %s'

            cursor.execute(calcSql, (calc_week, max_price2))
            data3 = cursor.fetchall()

            if len(data3) > 0:
                print("**** 결과 : 주별 가장 많은 금액을 주문한 고객 정보 *****")
                for row in data3:
                    print("* ----> 고객 ID: {0}/ 이름: {1}/ 이메일(아이디): {2}/ 주소: {3}/ 전화번호: {4}/ 총 주문 금액($): {5}".format(row['mem_id'], row['mem_name'], row['mem_email'], row['mem_address'], row['mem_phonenum'], row['sum(o.order_price)']))
            else:
                print("* {0}월 {1}주에 해당하는 검색 결과가 없습니다.".format(month, week))
        else:
            print("* {0}월 {1}주에 해당하는 검색 결과가 없습니다.".format(month, week))

    # 월별/주별 주문량이 가장 많은 핸드폰 정보 조회
    def show_max_order_phone(self):
        month = input("* 어떤 월을 기준으로 조회하시겠습니까? (ex: 1) : ")
        week = input("* 어떤 주를 기준으로 조회하시겠습니까? (ex: 2) : ")
        
        # 월별 
        selectSql = 'SELECT p.prod_id, p.prod_name, sum(o.order_qty) FROM order_mng o, product p WHERE o.prod_id = p.prod_id and MONTH(o.order_created_date) = %s GROUP BY p.prod_id'
        cursor.execute(selectSql, month)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "주문 수량"]

        qty_list = list()

        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['sum(o.order_qty)']])
                qty_list.append(row['sum(o.order_qty)'])
            print("*** {0}월의 상품별 총 주문 수량 조회 ***".format(month))
            print(table)
            max_qty = max(qty_list)

            selSql = 'SELECT p.prod_id, p.prod_name, p.prod_company, p.prod_color, p.prod_volume, sum(o.order_qty) FROM order_mng o, product p WHERE o.prod_id = p.prod_id and MONTH(o.order_created_date) = %s GROUP BY p.prod_id HAVING sum(o.order_qty) = %s'

            cursor.execute(selSql, (month, max_qty))
            data2 = cursor.fetchall()

            if len(data2) > 0:
                print("**** 결과 : 월별 주문이 가장 많은 핸드폰 정보 *****")
                for row in data2:
                    print("* ----> 상품 ID: {0}/ 상품명: {1}/ 제조사: {2}/ 색상: {3}/ 용량: {4}/ 총 주문 수량: {5}".format(row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['sum(o.order_qty)']))
            else:
                print("* {0}월에 해당하는 검색 결과가 없습니다.".format(month))
        else:
            print("* {0}월에 해당하는 검색 결과가 없습니다.".format(month))
        
        print("-" * 110)

        # 주별 
        calc_week = 4 * (int(month) - 1) + int(week)

        alldateSql = 'SELECT p.prod_id, p.prod_name, sum(o.order_qty) FROM order_mng o, product p WHERE o.prod_id = p.prod_id and week(o.order_created_date) = %s GROUP BY p.prod_id'
        cursor.execute(alldateSql, calc_week)
        alldate = cursor.fetchall()

        table2 = PrettyTable()
        table2.field_names = ["상품 ID", "상품명", "주문 수량"]

        week_qty_list = list()

        if len(alldate) > 0:
            for row in alldate:
                table2.add_row([row['prod_id'], row['prod_name'], row['sum(o.order_qty)']])
                week_qty_list.append(row['sum(o.order_qty)'])
            print("*** {0}월 {1}주의 상품별 총 주문 수량 조회 ***".format(month, week))
            print(table2)
            max_qty2 = max(week_qty_list)

            calcSql = 'SELECT p.prod_id, p.prod_name, p.prod_company, p.prod_color, p.prod_volume, sum(o.order_qty) FROM order_mng o, product p WHERE o.prod_id = p.prod_id and week(o.order_created_date) = %s GROUP BY p.prod_id HAVING sum(o.order_qty) = %s'

            cursor.execute(calcSql, (calc_week, max_qty2))
            data3 = cursor.fetchall()

            if len(data3) > 0:
                print("**** 결과 : 월별 주문이 가장 많은 핸드폰 정보 *****")
                for row in data3:
                    print("* ----> 상품 ID: {0}/ 상품명: {1}/ 제조사: {2}/ 색상: {3}/ 용량: {4}/ 총 주문 수량: {5}".format(row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['sum(o.order_qty)']))
            else:
                print("* {0}월 {1}주에 해당하는 검색 결과가 없습니다.".format(month, week))
        else:
            print("* {0}월 {1}주에 해당하는 검색 결과가 없습니다.".format(month, week))

    # 전체 핸드폰 리스트 조회
    def show_phone_list(self):
        selectSql = 'SELECT * FROM product'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "제조사", "색상", "용량(GB)", "가격($)", "수량", "등록 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['prod_price'], row['prod_qty'], row['prod_created_date']])
            print("*** 전체 핸드폰 목록 조회 ***")
            print(table)
        else:
            print("* 상품 검색 결과가 없습니다.")

    # 전체 고객 정보 보기
    def show_member_list(self):
        selectSql = 'SELECT * FROM member'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["고객 ID", "이름", "이메일(아이디)", "비밀번호", "주소", "전화번호", "가입 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['mem_id'], row['mem_name'], row['mem_email'], row['mem_pwd'], row['mem_address'], row['mem_phonenum'], row['mem_created_date']])
            print("*** 전체 고객 정보 조회 ***")
            print(table)
        else:
            print("* 회원 검색 결과가 없습니다.")

    # 전체 장바구니 목록 보기
    def show_shopbasket_list(self):
        od_selectSql = 'SELECT * FROM shopbasket s, product p, member m WHERE s.prod_id = p.prod_id and s.mem_id = m.mem_id'
        cursor.execute(od_selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["장바구니 ID", "고객 이름", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "수량", "가격($)", "장바구니 추가 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['sb_id'], row['mem_name'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['sb_qty'], row['sb_price'], row['sb_created_date']])
            print("*** 전체 장바구니 목록 조회 ***")
            print(table)
        else:
            print("* 검색 결과가 없습니다.")

    # new 핸드폰 정보 등록 
    def add_phone(self):
        p_name = input("* 상품명 : ")
        p_company = input("* 제조사 : ")
        p_color = input("* 색상 : ")
        p_volume = input("* 용량(GB) : ")
        p_price = input("* 가격($) : ")
        p_qty = input("* 수량 : ")

        insertSql = """INSERT INTO product(prod_name, prod_company, prod_color, prod_volume, prod_price, prod_qty, prod_created_date) VALUES(%s, %s, %s, %s, %s, %s, NOW())"""
        cursor.execute(insertSql, (p_name, p_company, p_color, p_volume, p_price, p_qty))
        conn.commit()
        print("* 새로운 핸드폰 정보가 등록되었습니다.")

    # 핸드폰 정보 수정
    def modify_phone(self):
        # 현재 핸드폰 목록 출력 
        selectSql = 'SELECT * FROM product'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "제조사", "색상", "용량(GB)", "가격($)", "수량", "등록 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['prod_price'], row['prod_qty'], row['prod_created_date']])
            print("*** 현재 핸드폰 목록 조회 ***")
            print(table)
            
            idNum = input("* 변경하고 싶은 핸드폰 정보의 ID를 입력해주세요. -> ")

            selSql = 'SELECT * FROM product WHERE prod_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()

            print("* 변경 내용을 아래에 작성해주세요 *")
            if(len(data) > 0):
                p_name = input("* 상품명 : ")
                p_company = input("* 제조사 : ")
                p_color = input("* 색상 : ")
                p_volume = input("* 용량(GB) : ")
                p_price = input("* 가격($) : ")
                p_qty = input("* 수량 : ")

                updateSql = 'UPDATE product SET prod_name = %s, prod_company = %s, prod_color = %s, prod_volume = %s, prod_price = %s, prod_qty = %s WHERE prod_id = %s'
                cursor.execute(updateSql, (p_name, p_company, p_color, p_volume, p_price, p_qty, int(idNum)))
                conn.commit()
                print("* 수정이 완료되었습니다. 전체 핸드폰 리스트를 확인해보세요.")
            else:
                print("* 입력하신 ID를 가진 핸드폰 정보는 존재하지 않습니다.")
        else:
            print("* 상품 검색 결과가 없어 수정할 수 없습니다.")

    # 핸드폰 정보 삭제
    def delete_phone(self):
        # 현재 핸드폰 목록 출력 
        selectSql = 'SELECT * FROM product'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "제조사", "색상", "용량(GB)", "가격($)", "수량", "등록 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['prod_price'], row['prod_qty'], row['prod_created_date']])
            print("*** 현재 핸드폰 목록 조회 ***")
            print(table)

            idNum = input("* 삭제하고 싶은 핸드폰 정보의 ID를 입력해주세요. -> ")

            selSql = 'SELECT * FROM product WHERE prod_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()
            if(len(data) > 0):
                deleteSql = 'DELETE FROM product WHERE prod_id = %s'
                cursor.execute(deleteSql, int(idNum))
                conn.commit()
                print("* 삭제가 완료되었습니다. 전체 핸드폰 리스트를 확인해보세요.")
            else:
                print("* 입력하신 ID를 가진 핸드폰 정보는 존재하지 않습니다.")
        else:
            print("* 상품 검색 결과가 없어 삭제할 수 없습니다.")

    # 고객 정보 수정
    def modify_member(self):
        # 현재 고객 리스트 출력 
        selectSql = 'SELECT * FROM member'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["고객 ID", "이름", "이메일(아이디)", "비밀번호", "주소", "전화번호", "가입 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['mem_id'], row['mem_name'], row['mem_email'], row['mem_pwd'], row['mem_address'], row['mem_phonenum'], row['mem_created_date']])
            print("*** 현재 고객 목록 조회 ***")
            print(table)

            idNum = input("* 수정하고 싶은 고객 정보의 ID를 입력해주세요. -> ")
            
            selSql = 'SELECT * FROM member WHERE mem_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()
            if(len(data) > 0):
                m_name = input("* 고객 이름 : ")
                m_email = input("* 고객 이메일(아이디) : ")
                m_pwd = input("* 고객 비밀번호 : ")
                m_address = input("* 고객 주소 : ")
                m_phone_num = input("* 고객 전화번호 : ")

                updateSql = 'UPDATE member SET mem_name = %s, mem_email = %s, mem_pwd = %s, mem_address = %s, mem_phonenum = %s WHERE mem_id = %s'
                cursor.execute(updateSql, (m_name, m_email, m_pwd, m_address, m_phone_num, int(idNum)))
                conn.commit()
                print("* 수정이 완료되었습니다. 전체 고객 리스트를 확인해보세요.")
            else:
                print("* 입력하신 ID를 가진 고객 정보는 존재하지 않습니다.")
        else:
            print("* 상품 검색 결과가 없어 수정할 수 없습니다.")

    # 고객 정보 삭제
    def delete_member(self):
        # 현재 고객 목록 출력 
        selectSql = 'SELECT * FROM member'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["고객 ID", "이름", "이메일(아이디)", "비밀번호", "주소", "전화번호", "가입 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['mem_id'], row['mem_name'], row['mem_email'], row['mem_pwd'], row['mem_address'], row['mem_phonenum'], row['mem_created_date']])
            print("*** 현재 고객 목록 조회 ***")
            print(table)

            idNum = input("* 삭제하고 싶은 고객 정보의 ID를 입력해주세요. -> ")

            selSql = 'SELECT * FROM member WHERE mem_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()
            if(len(data) > 0):
                deleteSql = 'DELETE FROM member WHERE mem_id = %s'
                cursor.execute(deleteSql, int(idNum))
                conn.commit()
                print("* 삭제가 완료되었습니다. 전체 고객 리스트를 확인해보세요.")
            else:
                print("* 입력하신 ID를 가진 고객 정보는 존재하지 않습니다.")
        else:
            print("* 상품 검색 결과가 없어 삭제할 수 없습니다.")

# 주문 클래스 
class Order:
    # 핸드폰 주문
    def order_phone(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()
        # 전체 핸드폰 목록 출력
        selectSql = 'SELECT * FROM product'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "제조사", "색상", "용량(GB)", "가격($)", "수량", "등록 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['prod_price'], row['prod_qty'], row['prod_created_date']])
            print("*** 전체 핸드폰 목록 조회 ***")
            print(table)
        else:
            print("* 검색 결과가 없습니다.")

        # 주문서 입력 
        idNum = input("* 주문할 핸드폰 정보의 ID를 입력해주세요. -> ")
        while True:
            qtyNum = input("* 원하는 수량을 입력해주세요. -> ")
            if int(qtyNum) >= 1:
                break
            else:
                print("* 1개 이상의 수량을 입력해주세요.")

        # 상품 목록 검색 
        selectSql = 'SELECT * FROM product WHERE prod_id = %s'
        cursor.execute(selectSql, idNum)
        data = cursor.fetchall()

        if len(data) > 0:
            for row in data:
                phone_price = int(row['prod_price'])
                phone_name = row['prod_name']
                phone_qty = int(row['prod_qty'])
            # 수량 충분 -> 구매 가능
            if phone_qty >= int(qtyNum):
                # 주문 
                insertSql = """INSERT INTO order_mng(prod_id, order_qty, order_price , mem_id, order_created_date) VALUES(%s, %s, %s, %s, NOW())"""
                cursor.execute(insertSql, (idNum, int(qtyNum), (int(qtyNum) * phone_price), login_info.mem_id))
                conn.commit()

                # 주문한 핸드폰 개수만큼 product 테이블의 핸드폰 개수 감소 처리
                updateSql = 'UPDATE product SET prod_qty = %s WHERE prod_id = %s'
                cursor.execute(updateSql, ((phone_qty - int(qtyNum)), idNum))
                conn.commit()

                print("* 주문이 완료되었습니다! 주문내역을 확인해주세요.")
            # 수량 부족 -> 구매 불가능
            else:
                if phone_qty > 0:
                    print("* 수량이 부족하여 주문이 불가능한 상태입니다.")
                    choice = input("* 현재 최대 {0}개까지 구매가 가능합니다. 최대 수량으로 구매하시겠습니까? (예: y, 아니요: n) : ".format(phone_qty))
                    if choice == 'y':
                        # 주문 
                        insertSql_s = """INSERT INTO order_mng(prod_id, order_qty, order_price , mem_id, order_created_date) VALUES(%s, %s, %s, %s, NOW())"""
                        cursor.execute(insertSql_s, (idNum, phone_qty, (phone_qty * phone_price), login_info.mem_id))
                        conn.commit()

                        # 주문한 핸드폰 개수만큼 product 테이블의 핸드폰 개수 감소 처리
                        updateSql_s = 'UPDATE product SET prod_qty = %s WHERE prod_id = %s'
                        cursor.execute(updateSql_s, ((phone_qty - phone_qty), idNum))
                        conn.commit()

                        print("* 주문이 완료되었습니다! 주문내역을 확인해주세요.")
                    else:
                        if choice == 'n':
                            print("* 주문이 취소되었습니다.")
                        else:
                            print("* y 또는 n을 입력해주세요.")
                else:
                    print("* 수량이 부족하여 주문이 불가능한 상태입니다.")
        else:
            print("* 핸드폰 목록이 없어 주문이 불가능합니다.")
            
    # 주문 내역 조회
    def show_order_list(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        od_selectSql = 'SELECT * FROM order_mng o, product p WHERE o.prod_id = p.prod_id and mem_id = %s'
        cursor.execute(od_selectSql, (login_info.mem_id))
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["주문 ID", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "주문 수량", "주문 금액($)", "주문 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['order_id'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['order_qty'], row['order_price'], row['order_created_date']])
            print("*** 주문 내역 조회 ***")
            print(table)
        else:
            print("* 검색 결과가 없습니다.")

    # 주문 변경 
    def modify_order(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        # 주문 내역 출력 
        od_selectSql = 'SELECT * FROM order_mng o, product p WHERE o.prod_id = p.prod_id and mem_id = %s'
        cursor.execute(od_selectSql, (login_info.mem_id))
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["주문 ID", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "주문 수량", "주문 금액($)", "주문 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['order_id'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['order_qty'], row['order_price'], row['order_created_date']])
            print("*** 주문 내역 조회 ***")
            print(table)

            # 주문 변경
            idNum = input("* 변경하고 싶은 주문 내역의 ID를 입력해주세요. -> ")
            print("-" * 50)
            modNum = input("* 변경하고 싶은 상품의 ID를 입력해주세요. -> ")
            while True:
                qtyNum = input("* 원하는 수량을 입력해주세요. -> ")
                if int(qtyNum) >= 1:
                    break
                else:
                    print("* 1개 이상의 수량을 입력해주세요.")

            # 주문 내역 검색 
            selectSql = 'SELECT * FROM order_mng WHERE order_id = %s'
            cursor.execute(selectSql, idNum)
            data = cursor.fetchall()

            now_order_qty = 0
            if len(data) > 0:
                for row in data:
                    now_order_qty = int(row['order_qty'])
                # 상품 목록 검색 
                selectSql = 'SELECT * FROM product WHERE prod_id = %s'
                cursor.execute(selectSql, int(modNum))
                data = cursor.fetchall()

                phone_price = 0
                phone_qty = 0

                if len(data) > 0:
                    for row in data:
                        phone_price = int(row['prod_price'])
                        phone_qty = int(row['prod_qty'])
                else:
                    print("* 검색 결과가 없습니다.")

                if now_order_qty <= int(qtyNum):
                    if int(qtyNum) <= (now_order_qty + phone_qty):
                        # 주문 변경
                        updateSql = 'UPDATE order_mng SET prod_id = %s, order_qty = %s, order_price = %s WHERE order_id = %s'
                        cursor.execute(updateSql, (int(modNum), int(qtyNum), (phone_price * int(qtyNum)), idNum))
                        conn.commit()

                        # 주문한 핸드폰 개수만큼 product 테이블의 핸드폰 개수 Update
                        updateSql = 'UPDATE product SET prod_qty = %s WHERE prod_id = %s'
                        cursor.execute(updateSql, ((phone_qty - (int(qtyNum) - now_order_qty)), int(modNum)))
                        conn.commit()

                        print("* 주문 변경이 완료되었습니다! 주문내역을 확인해주세요.")
                    else:
                        print("* 수량 부족으로 인해 주문 변경이 불가능합니다.")
                else:
                    if now_order_qty > int(qtyNum):
                        if int(qtyNum) <= (now_order_qty + phone_qty):
                            # 주문 변경
                            updateSql = 'UPDATE order_mng SET prod_id = %s, order_qty = %s, order_price = %s WHERE order_id = %s'
                            cursor.execute(updateSql, (int(modNum), int(qtyNum), (phone_price * int(qtyNum)), idNum))
                            conn.commit()

                            # 주문한 핸드폰 개수만큼 product 테이블의 핸드폰 개수 Update
                            updateSql = 'UPDATE product SET prod_qty = %s WHERE prod_id = %s'
                            cursor.execute(updateSql, ((phone_qty + (now_order_qty - int(qtyNum))), int(modNum)))
                            conn.commit()

                            print("* 주문 변경이 완료되었습니다! 주문내역을 확인해주세요.")
                        else:
                            print("* 수량 부족으로 인해 주문 변경이 불가능합니다.")    
                    else:
                        print("* 수량 부족으로 인해 주문 변경이 불가능합니다.")
            else:
                print("* 변경할 주문 내역이 존재하지 않습니다.")
        else:
            print("* 변경할 주문 내역이 존재하지 않습니다.")

    # 주문 취소
    def delete_order(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        # 현 사용자의 주문 내역 출력 
        selectSql = 'SELECT * FROM order_mng o, product p WHERE o.prod_id = p.prod_id and mem_id = %s'
        cursor.execute(selectSql, (login_info.mem_id))
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["주문 ID", "상품 ID", "상품명", "제조사", "색상", "용량(GB)", "주문 수량", "주문 금액($)", "주문 날짜"]

        if len(data) > 0:
            for row in data:
                table.add_row([row['order_id'], row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['order_qty'], row['order_price'], row['order_created_date']])
            print("*** 주문 내역 조회 ***")
            print(table)

            idNum = input("* 취소할 주문 내역의 ID를 입력해주세요. -> ")

            selSql = 'SELECT * FROM order_mng WHERE order_id = %s'
            cursor.execute(selSql, int(idNum))
            data = cursor.fetchall()

            need_id = 0
            need_order_qty = 0
            phone_qty = 0

            if len(data) > 0:
                for row in data:
                    need_id = int(row['prod_id'])
                    need_order_qty = int(row['order_qty'])
                # 상품 목록 검색 
                selectSql = 'SELECT * FROM product WHERE prod_id = %s'
                cursor.execute(selectSql, (need_id))
                data = cursor.fetchall()

                if len(data) > 0:
                    for row in data:
                        phone_qty = int(row['prod_qty'])
                    # 주문 내역 삭제
                    deleteSql = 'DELETE FROM order_mng WHERE order_id = %s'
                    cursor.execute(deleteSql, int(idNum))
                    conn.commit()

                    # 취소한 핸드폰 개수만큼 product 테이블의 핸드폰 개수 증가 처리
                    updateSql = 'UPDATE product SET prod_qty = %s WHERE prod_id = %s'
                    cursor.execute(updateSql, ((phone_qty + need_order_qty), need_id))
                    conn.commit()
                    print("* 주문 취소가 완료되었습니다.") 
                else:
                    print("* 검색 결과가 없습니다.")
            else:
                print("* 검색 결과가 없습니다.")
        else:
            print("* 취소할 주문 내역이 존재하지 않습니다.")

# 상품 클래스 
class Item:
    # 전체 핸드폰 리스트 조회
    def show_phone_list(self):
        selectSql = 'SELECT * FROM product'
        cursor.execute(selectSql)
        data = cursor.fetchall()

        table = PrettyTable()
        table.field_names = ["상품 ID", "상품명", "제조사", "색상", "용량(GB)", "가격($)", "수량", "등록 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['prod_id'], row['prod_name'], row['prod_company'], row['prod_color'], row['prod_volume'], row['prod_price'], row['prod_qty'], row['prod_created_date']])
            print("*** 전체 핸드폰 목록 조회 ***")
            print(table)
        else:
            print("* 검색 결과가 없습니다.")
    
# 고객 클래스 
class Member:
    # 회원 정보 수정 
    def modify_member(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        # 현재 사용자 정보 출력 
        selectSql = 'SELECT * FROM member WHERE mem_id = %s'
        cursor.execute(selectSql, login_info.mem_id)
        data = cursor.fetchall()
        print(len(data))

        table = PrettyTable()
        table.field_names = ["고객 ID", "이름", "이메일(아이디)", "비밀번호", "주소", "전화번호", "가입 날짜"]
        
        if len(data) > 0:
            for row in data:
                table.add_row([row['mem_id'], row['mem_name'], row['mem_email'], row['mem_pwd'], row['mem_address'], row['mem_phonenum'], row['mem_created_date']])
            print("*** 현재 사용자 정보 조회 ***")
            print(table)

            # 수정하고자 하는 정보 입력 
            u_answer = input("* 회원 정보를 수정하시겠습니까? (예: y, 아니요: n) -> ")
            if u_answer == 'y':
                print("* 변경 내용을 아래에 작성해주세요 *")
                print("******************회원 정보 변경******************")
                c_name = input("* 이름 : ")
                c_email = input("* 이메일(아이디) : ")
                c_pwd = input("* 비밀번호 : ")
                c_address = input("* 주소 : ")
                c_phone = input("* 전화번호 : ")

                # 회원 정보 수정 
                updateSql = 'UPDATE member SET mem_name = %s, mem_email = %s, mem_pwd = %s, mem_address = %s, mem_phonenum = %s WHERE mem_id = %s'
                cursor.execute(updateSql, (c_name, c_email, c_pwd, c_address, c_phone, login_info.mem_id))
                conn.commit()
                print("* 회원 정보 수정이 완료되었습니다.")

                # 수정 후 사용자의 정보 출력 
                selectSql = 'SELECT * FROM member WHERE mem_id = %s'
                cursor.execute(selectSql, login_info.mem_id)
                data = cursor.fetchall()
                
                table2 = PrettyTable()
                table2.field_names = ["고객 ID", "이름", "이메일(아이디)", "비밀번호", "주소", "전화번호", "가입 날짜"]
                
                if len(data) > 0:
                    for row in data:
                        table2.add_row([row['mem_id'], row['mem_name'], row['mem_email'], row['mem_pwd'], row['mem_address'], row['mem_phonenum'], row['mem_created_date']])
                        # 현재 사용자 정보 업데이트 
                        login_info.setUserData(row['mem_id'], row['mem_email'], row['mem_pwd'])
                    print(table2)
                else:
                    print("* 검색 결과가 없습니다.")
            else:
                if u_answer == 'n':
                    print("* 회원 정보 수정을 취소하셨습니다.")
                else:
                    print("* y 또는 n을 입력해주세요.")
        else:
            print("* 검색 결과가 없습니다.")

    # 회원 가입 
    def sign_up(self):
        u_name = input("* 이름 : ")
        u_email = input("* 이메일(아이디) : ")
        u_pwd = input("* 비밀번호 : ")
        u_address = input("* 주소 : ")
        u_phone = input("* 전화번호 : ")

        insertSql = """INSERT INTO member(mem_name, mem_email, mem_pwd, mem_address, mem_phonenum, mem_created_date) VALUES(%s, %s, %s, %s, %s, NOW())"""
        cursor.execute(insertSql, (u_name, u_email, u_pwd, u_address, u_phone))
        conn.commit()

        # Member 테이블 안에 등록한 사용자 이름이 존재하는지 판단 
        selectSql = 'SELECT mem_name FROM member WHERE mem_name = %s and mem_phonenum = %s'
        cursor.execute(selectSql, (u_name, u_phone))
        data = cursor.fetchall()
        print(data)

        for row in data:
            if u_name == row['mem_name']:
                print("* 회원가입이 완료되었습니다.")
            else:
                print("* 회원가입에 실패하였습니다. 다시 시도해주세요.")

    # 회원 탈퇴
    def remove_member(self):
        # 현재 로그인한 사용자 정보 
        login_info = UserLogin()

        u_answer = input("* 정말로 탈퇴하시겠습니까? (예: y, 아니요: n) -> ")
        if u_answer == 'y':
            while True:
                u_pwd = input("* 비밀번호 입력 : ")
                if u_pwd == login_info.mem_pwd:
                    # 회원 삭제 
                    deleteSql = 'DELETE FROM member WHERE mem_id = %s'
                    cursor.execute(deleteSql, login_info.mem_id)
                    conn.commit()
                    print("* 회원 탈퇴가 완료되었습니다. 다음에 또 찾아주세요!") 
                    return 1
                else:
                    print("* 비밀번호가 일치하지 않습니다.")
                    return 0
        else:
            if u_answer == 'n':
                print("* 회원 탈퇴를 취소하셨습니다.")
                return 0
            else:
                print("* y 또는 n을 입력해주세요.")
                return 0 

    # 회원 로그인 
    def sign_in(self):        
        u_email = input("* 이메일(아이디) : ")
        u_pwd = input("* 비밀번호 : ")

        selectSql = 'SELECT mem_id, mem_name, mem_email, mem_pwd FROM member WHERE mem_email = %s and mem_pwd = %s and mem_email != %s and mem_pwd != %s'
        cursor.execute(selectSql, (u_email, u_pwd, 'admin', 'admin1234'))
        data = cursor.fetchall()

        if len(data) == 0:
            return 0
        else:
            login_info = UserLogin()
            for row in data:
                print("---------------------------------------------------------------")
                print("* 로그인 성공! '{0}'님 안녕하세요!".format(row['mem_name']))
                login_info.setUserData(row['mem_id'], row['mem_email'], row['mem_pwd'])
            return 1
        
def main():
    # Member, Item, Order, ShopBasket 클래스의 인스턴스 생성
    member = Member()
    item = Item()
    order = Order()
    basket = ShopBasket()

    while True:
        userNum = input('''
***************************************************************
***   ***   ***   ***   ***   ***   ***   ***   ***   ***   ***
******   ***   ***   ***   ***   ***   ***   ***   ***   ******
***   ***   ***    WELCOME TO " PHONE SHOP "    ***   ***   ***
******   ***   ***   ***   ***   ***   ***   ***   ***   ******
***   ***   ***   ***   ***   ***   ***   ***   ***   ***   ***
***************************************************************
# 1. 회원 로그인
# 2. 회원가입
# 3. 종료
# 0. 관리자 로그인
---------------------------------------------------------------
메뉴를 선택하세요 (0-3) -> ''')
    
        # 사용자 로그인 
        if userNum == '1':
            result = member.sign_in()
            
            # 로그인 성공시 사용자 화면 접속
            if result == 1:
                while True:
                    cert_userNum = input('''
***************************************************************
************************** USER *******************************
***************************************************************
# 1. 핸드폰 목록 조회
# 2. 핸드폰 주문
# 3. 장바구니 추가
# 4. 장바구니 조회
# 5. 장바구니 취소
# 6. 주문 내역 조회
# 7. 주문 변경
# 8. 주문 취소
# 9. 개인정보 수정
# 10. 회원 탈퇴
# 11. 로그아웃
---------------------------------------------------------------
메뉴를 선택하세요 (1-11) -> ''')

                    if cert_userNum == '1':
                        item.show_phone_list()
                    if cert_userNum == '2':
                        order.order_phone()
                    if cert_userNum == '3':
                        basket.add_shopbasket()
                    if cert_userNum == '4':
                        basket.show_shopbasket()
                    if cert_userNum == '5':
                        basket.delete_shopbasket()
                    if cert_userNum == '6':
                        order.show_order_list()
                    if cert_userNum == '7':
                        order.modify_order()
                    if cert_userNum == '8':
                        order.delete_order()
                    if cert_userNum == '9':
                        member.modify_member()
                    if cert_userNum == '10':
                        rslt = member.remove_member()
                        if rslt == 1:
                            # 현재 로그인한 사용자 정보 
                            login_info = UserLogin()
                            login_info.setUserData(" ", " ", " ")
                            break
                    if cert_userNum == '11':
                        # 현재 로그인한 사용자 정보 
                        login_info = UserLogin()
                        login_info.setUserData(" ", " ", " ")
                        print("* 로그아웃 되었습니다.")
                        break
                    if cert_userNum != '1' and cert_userNum != '2' and cert_userNum != '3' and cert_userNum != '4' and cert_userNum != '5' and cert_userNum != '6' and cert_userNum != '7' and cert_userNum != '8' and cert_userNum != '9' and cert_userNum != '10' and cert_userNum != '11':
                        print("* 1 ~ 11 사이의 숫자를 입력해주세요!")
            else:
                print("* 로그인 실패! 다시 시도하세요.")
        # 회원가입 
        if userNum == '2':
            member.sign_up()
        # 종료 
        if userNum == '3':
            # cursor, conn 연결 끊기  
            cursor.close()
            conn.close()
            print("**** PHONE SHOP ***** 프로그램이 종료되었습니다.")
            break
        # 관리자 로그인
        if userNum == '0':
            admin = Admin()
            a_rslt = admin.admin_sign_in()
            # 로그인 성공시 관리자 화면 접속 
            if a_rslt == 1:
                while True:
                    adminNum = input('''
***************************************************************
************************** ADMIN ******************************
***************************************************************
# 1. 전체 핸드폰 목록 조회
# 2. 전체 고객 목록 조회
# 3. 전체 주문 내역 조회
# 4. 고객별 주문 내역 조회
# 5. 전체 장바구니 내역 조회
# 6. 월별/주별 가장 많은 금액을 주문한 고객 정보 조회
# 7. 월별/주별 가장 많이 주문된 상품 정보 조회
# 8. 핸드폰 정보 등록
# 9. 핸드폰 정보 수정
# 10. 핸드폰 정보 삭제
# 11. 고객 정보 수정
# 12. 고객 정보 삭제
# 13. 로그아웃
---------------------------------------------------------------
메뉴를 선택하세요 (1-13) -> ''')

                    if adminNum == '1':
                        admin.show_phone_list()
                    if adminNum == '2':
                        admin.show_member_list()
                    if adminNum == '3':
                        admin.show_order_list()
                    if adminNum == '4':
                        admin.show_order_bymember()
                    if adminNum == '5':
                        admin.show_shopbasket_list()
                    if adminNum == '6':
                        admin.show_max_price_member()
                    if adminNum == '7':
                        admin.show_max_order_phone()
                    if adminNum == '8':
                        admin.add_phone()
                    if adminNum == '9':
                        admin.modify_phone()
                    if adminNum == '10':
                        admin.delete_phone()
                    if adminNum == '11':
                        admin.modify_member()
                    if adminNum == '12':
                        admin.delete_member()
                    if adminNum == '13':
                        # 현재 로그인한 사용자 정보 
                        login_info = UserLogin()
                        login_info.setUserData(" ", " ", " ")
                        print("* 로그아웃 되었습니다.")
                        break
                    if adminNum != '1' and adminNum != '2' and adminNum != '3' and adminNum != '4' and adminNum != '5' and adminNum != '6' and adminNum != '7' and adminNum != '8' and adminNum != '9' and adminNum != '10' and adminNum != '11' and adminNum != '12' and adminNum != '13':
                        print("* 1 ~ 13 사이의 숫자를 입력해주세요!")
            else:
                print("* 관리자 로그인 실패! 다시 시도하세요.")
        if userNum != '1' and userNum != '2' and userNum != '3' and userNum != '0':
            print("* 0 ~ 3 사이의 숫자를 입력해주세요!")

main()