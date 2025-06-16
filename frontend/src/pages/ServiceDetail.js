import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ServiceDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [orderLoading, setOrderLoading] = useState(false);
  const [orderRequirements, setOrderRequirements] = useState('');

  useEffect(() => {
    fetchService();
  }, [id]);

  const fetchService = async () => {
    try {
      const response = await axios.get(`${API}/services/${id}`);
      setService(response.data);
    } catch (error) {
      console.error('Error fetching service:', error);
      setError('Service not found');
    } finally {
      setLoading(false);
    }
  };

  const handleOrder = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (user.user_type !== 'buyer') {
      setError('Only buyers can place orders');
      return;
    }

    if (!orderRequirements.trim()) {
      setError('Please provide order requirements');
      return;
    }

    setOrderLoading(true);
    setError('');

    try {
      // This would be implemented when we add the order management system
      console.log('Order placed:', {
        service_id: service.id,
        requirements: orderRequirements
      });
      
      // For now, show success message
      alert('Order functionality will be available soon! Your request has been noted.');
      
    } catch (error) {
      console.error('Error placing order:', error);
      setError('Failed to place order');
    } finally {
      setOrderLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !service) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Service Not Found</h2>
          <p className="text-gray-600 mb-6">The service you're looking for doesn't exist.</p>
          <button
            onClick={() => navigate('/marketplace')}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Back to Marketplace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              {/* Service Images */}
              <div className="mb-6">
                {service.images && service.images.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {service.images.map((image, index) => (
                      <img 
                        key={index}
                        src={`data:image/jpeg;base64,${image}`} 
                        alt={`${service.title} - Image ${index + 1}`}
                        className="w-full h-64 object-cover rounded-lg"
                      />
                    ))}
                  </div>
                ) : (
                  <div className="h-64 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <div className="text-white text-center">
                      <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <p className="text-lg font-medium">{service.title}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Service Title and Category */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {service.category.split('-').map(word => 
                      word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ')}
                  </span>
                </div>
                <h1 className="text-3xl font-bold text-gray-900 mb-4">{service.title}</h1>
                
                {/* Tags */}
                {service.tags && service.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {service.tags.map((tag, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Service Description */}
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-3">About This Service</h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {service.description}
                </p>
              </div>

              {/* Service Details */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">⏱️</div>
                  <p className="font-semibold text-gray-900">{service.delivery_time_days} Days</p>
                  <p className="text-gray-600 text-sm">Delivery Time</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">🔄</div>
                  <p className="font-semibold text-gray-900">{service.revisions_included}</p>
                  <p className="text-gray-600 text-sm">Revisions Included</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <div className="text-2xl mb-2">💰</div>
                  <p className="font-semibold text-gray-900">${service.base_price}</p>
                  <p className="text-gray-600 text-sm">Starting Price</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <div className="text-center mb-6">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  ${service.base_price}
                </div>
                <p className="text-gray-600">Starting at</p>
              </div>

              {user && user.user_type === 'buyer' && user.id !== service.creator_id ? (
                <div className="space-y-4">
                  {error && (
                    <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                      {error}
                    </div>
                  )}
                  
                  <div>
                    <label htmlFor="requirements" className="block text-sm font-medium text-gray-700 mb-2">
                      Order Requirements
                    </label>
                    <textarea
                      id="requirements"
                      value={orderRequirements}
                      onChange={(e) => setOrderRequirements(e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Describe what you need for this project..."
                    />
                  </div>
                  
                  <button
                    onClick={handleOrder}
                    disabled={orderLoading || !orderRequirements.trim()}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    {orderLoading ? 'Processing...' : 'Order Now'}
                  </button>
                </div>
              ) : user && user.id === service.creator_id ? (
                <div className="text-center">
                  <p className="text-gray-600 mb-4">This is your service</p>
                  <button className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-md font-semibold">
                    Edit Service
                  </button>
                </div>
              ) : user && user.user_type === 'creator' ? (
                <div className="text-center">
                  <p className="text-gray-600 mb-4">
                    Only buyers can order services. Switch to a buyer account to place orders.
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <p className="text-gray-600 mb-4">Sign in to order this service</p>
                  <button
                    onClick={() => navigate('/login')}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 font-semibold"
                  >
                    Sign In
                  </button>
                </div>
              )}

              {/* Service Features */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-4">What's Included</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {service.delivery_time_days} day delivery
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {service.revisions_included} revision{service.revisions_included !== 1 ? 's' : ''}
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Professional quality work
                  </li>
                  <li className="flex items-center">
                    <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    Direct communication with creator
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetail;