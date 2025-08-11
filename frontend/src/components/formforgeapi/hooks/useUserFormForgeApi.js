// frontend/src/components/formforgeapi/hooks/useUserFormForgeApi.js
import { useState, useCallback } from 'react';
import FormForgeApiApi from '../api/FormForgeApiApi';

/**
 * FormForge kullanıcılarını yönetmek için özelleştirilmiş hook.
 * Sorumlulukları:
 * 1. API'den kullanıcı listesini çekmek.
 * 2. Veriyi 'react-select' gibi bileşenler için formatlamak.
 * 3. Yüklenme (loading) ve hata durumlarını yönetmek.
 * @returns {{
 * userList: Array<{value: number, label: string}>,
 * loading: boolean,
 * error: string | null,
 * fetchUserList: () => Promise<void>
 * }}
 */
export const useUserFormForgeApi = () => {
    const [userList, setUserList] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchUserList = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await FormForgeApiApi.getUsers();
            // API'den gelen veriyi react-select'in beklediği formata dönüştür
            const formattedUsers = response.data.results.map(user => ({
                value: user.id,
                label: user.email,
            }));
            setUserList(formattedUsers);
        } catch (err) {
            setError("Kullanıcı listesi getirilirken bir hata oluştu.");
            console.error("useUserFormForgeApi Hatası:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        userList,
        loading,
        error,
        fetchUserList,
    };
};

